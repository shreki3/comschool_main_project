import logging

# ლოგერის კონფიგურაცია, რომელიც ჩაწერს როგორც ფაილში, ისე კონსოლში
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hotel_bookings.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class Room:
    def __init__(self, room_number: int, room_type: str, price_per_night: float, max_guests: int):
        self.room_number = room_number
        self.room_type = room_type  # Single, Double, Suite
        self.price_per_night = price_per_night
        self.is_available = True
        self.max_guests = max_guests

    def book_room(self):
        if self.is_available:
            self.is_available = False
            return True
        return False

    def release_room(self):
        self.is_available = True

    def calculate_price(self, nights: int) -> float:
        # სეზონური/დინამიური ფასწარმოქმნა: თუ ჯავშნის 5 ღამეზე მეტს, იღებს 10%-იან ფასდაკლებას
        base_price = self.price_per_night * nights
        if nights >= 5:
            return round(base_price * 0.9, 2)
        return round(base_price, 2)

    def __str__(self):
        status = "თავისუფალი" if self.is_available else "დაკავებული"
        return f"ოთახი N{self.room_number} ({self.room_type}) - {self.price_per_night}₾/ღამე | სტატუსი: {status} | მაქს. სტუმარი: {self.max_guests}"


class Customer:
    def __init__(self, name: str, budget: float):
        self.name = name
        self.budget = budget
        self.booked_rooms = []  # ინახავს დაჯავშნილ Room ობიექტებს
        self.reward_points = 0

    def add_room(self, room: Room):
        if room not in self.booked_rooms:
            self.booked_rooms.append(room)

    def remove_room(self, room: Room):
        if room in self.booked_rooms:
            self.booked_rooms.remove(room)

    def pay_for_booking(self, total_price: float) -> bool:
        if self.budget >= total_price:
            self.budget -= total_price
            # ქულების დაგროვების სისტემა: ყოველ დახარჯულ 10 ₾-ზე 1 ქულა
            earned_points = int(total_price // 10)
            self.reward_points += earned_points
            return True
        return False

    def show_booking_summary(self) -> str:
        if not self.booked_rooms:
            return f"მომხმარებელს {self.name} არ აქვს დაჯავშნილი ოთახები."
        
        rooms_str = ", ".join([f"N{r.room_number} ({r.room_type})" for r in self.booked_rooms])
        return (f"მომხმარებელი: {self.name} | ბიუჯეტი: {self.budget}₾ | "
                f"დაჯავშნილი ოთახები: [{rooms_str}] | დაგროვილი ქულები: {self.reward_points}")


class Hotel:
    def __init__(self, name: str):
        self.name = name
        self.rooms = []  # Room ობიექტების სია
        self.bookings_log = []  # დაჯავშნის ისტორია

    def add_room(self, room: Room):
        self.rooms.append(room)

    def show_available_rooms(self, room_type: str = None) -> list:
        available = [r for r in self.rooms if r.is_available]
        if room_type:
            available = [r for r in available if r.room_type.lower() == room_type.lower()]
        return available

    def calculate_total_booking(self, room_number: int, nights: int) -> float:
        for r in self.rooms:
            if r.room_number == room_number:
                return r.calculate_price(nights)
        return 0.0

    def log_booking(self, customer: Customer, room: Room, total_price: float):
        log_msg = f"წარმატებული ჯავშანი: კლიენტი: {customer.name} | ოთახი N{room.room_number} ({room.room_type}) | თანხა: {total_price}₾"
        self.bookings_log.append(log_msg)
        logging.info(log_msg)

    def book_room_for_customer(self, customer: Customer, room_number: int, nights: int) -> bool:
        # მოვიძიოთ ოთახი
        selected_room = None
        for r in self.rooms:
            if r.room_number == room_number:
                selected_room = r
                break

        if not selected_room:
            logging.error(f"ოთახი N{room_number} ვერ მოიძებნა.")
            return False

        if not selected_room.is_available:
            logging.warning(f"დაჯავშნა ჩაიშალა: ოთახი N{room_number} უკვე დაკავებულია.")
            return False

        total_price = selected_room.calculate_price(nights)

        # გადახდის შემოწმება და ბიუჯეტის ჩამოჭრა
        if customer.pay_for_booking(total_price):
            selected_room.book_room()
            customer.add_room(selected_room)
            self.log_booking(customer, selected_room, total_price)
            return True
        else:
            logging.warning(f"დაჯავშნა ჩაიშალა: კლიენტს {customer.name} არ აქვს საკმარისი ბიუჯეტი ({total_price}₾ სჭირდება).")
            return False

    def cancel_booking(self, customer: Customer, room_number: int):
        selected_room = None
        for r in customer.booked_rooms:
            if r.room_number == room_number:
                selected_room = r
                break

        if selected_room:
            selected_room.release_room()
            customer.remove_room(selected_room)
            log_msg = f"ჯავშნის გაუქმება: კლიენტი: {customer.name} | ოთახი N{room_number}"
            self.bookings_log.append(log_msg)
            logging.info(log_msg)
            return True
        
        logging.warning(f"გაუქმება ჩაიშალა: კლიენტს {customer.name} არ აქვს დაჯავშნილი ოთახი N{room_number}")
        return False