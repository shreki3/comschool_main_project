import logging

# ლოგერის ვწერ  ფაილში და კონსოლში
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hotel_bookings.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class Room:
    # საწყისი ატრიბუტები ინიტისთვის
    def __init__(self, room_number: int, room_type: str, price_per_night: float, max_guests: int):
        self.room_number = room_number
        self.room_type = room_type  # Single, Double, Suite
        self.price_per_night = price_per_night
        self.is_available = True
        self.max_guests = max_guests

    # ვნიშნავ ოთახს დაკავებულად დაჯავშნის დროს
    def book_room(self):
        if self.is_available:
            self.is_available = False
            return True
        return False

    # ოთახს ჯავშნის გაუქმება
    def release_room(self):
        self.is_available = True

    #ვითვლი ჯამურ ფასს დღეების მიხედვით და ვითვალისწინებ 10%-იან ფასდაკლებას 5+ ღამეზე
    def calculate_price(self, nights: int) -> float:
        #5ზე მეტი ღამე
        base_price = self.price_per_night * nights
        if nights >= 5:
            return round(base_price * 0.9, 2)
        return round(base_price, 2)

    # ვაბრუნებ ოთახის ინფოს სტრინგად
    def __str__(self):
        status = "თავისუფალი" if self.is_available else "დაკავებული"
        return f"ოთახი N{self.room_number} ({self.room_type}) - {self.price_per_night}₾/ღამე | სტატუსი: {status} | მაქს. სტუმარი: {self.max_guests}"


class Customer:
    # იუზერის საწყისი მონაცემები
    def __init__(self, name: str, budget: float):
        self.name = name
        self.budget = budget
        self.booked_rooms = []  #დაჯავშნილი ოთახების სია
        self.reward_points = 0  #ქულები

    # დაჯავშნილი ოთახების სიაში დამატება
    def add_room(self, room: Room):
        if room not in self.booked_rooms:
            self.booked_rooms.append(room)

    # დაჯავშნილი ოტახების სიიდან ამოშლა
    def remove_room(self, room: Room):
        if room in self.booked_rooms:
            self.booked_rooms.remove(room)

    # ვაკლებ ბიუჯეტს თანხას და ვანგარიშობ ქულებს. 
    def pay_for_booking(self, total_price: float) -> bool:
        if self.budget >= total_price:
            self.budget -= total_price
            earned_points = int(total_price // 10)
            self.reward_points += earned_points
            return True
        return False

    # ვაბრუნებ  ბალანსს, ქულებს და დაჯავშნილ ოთახებს
    def show_booking_summary(self) -> str:
        if not self.booked_rooms:
            return f"მომხმარებელს {self.name} არ აქვს დაჯავშნილი ოთახები."
        
        rooms_str = ", ".join([f"N{r.room_number} ({r.room_type})" for r in self.booked_rooms])
        return (f"მომხმარებელი: {self.name} | ბიუჯეტი: {self.budget}₾ | "
                f"დაჯავშნილი ოთახები: [{rooms_str}] | ქულები: {self.reward_points}")


class Hotel:
    def __init__(self, name: str):
        self.name = name
        self.rooms = [] 
        self.bookings_log = []  

    # სასტუმროში ახალი ოთახის  დამატება
    def add_room(self, room: Room):
        self.rooms.append(room)

    # ვაბრუნებ ყველა თავისუფალი ოთახის სიას
    def show_available_rooms(self, room_type: str = None) -> list:
        available = [r for r in self.rooms if r.is_available]
        if room_type:
            available = [r for r in available if r.room_type.lower() == room_type.lower()]
        return available

    # ოთახის მიხედვით ფასის გამოთვლა
    def calculate_total_booking(self, room_number: int, nights: int) -> float:
        for r in self.rooms:
            if r.room_number == room_number:
                return r.calculate_price(nights)
        return 0.0

    # წარმატებული დაჯავშნის დალოგვა
    def log_booking(self, customer: Customer, room: Room, total_price: float):
        log_msg = f"წარმატებული ჯავშანი: კლიენტი: {customer.name} | ოთახი N{room.room_number} ({room.room_type}) | თანხა: {total_price}₾"
        self.bookings_log.append(log_msg)
        logging.info(log_msg)

    #შემოწმება, გადახდა, დალოგვა
    def book_room_for_customer(self, customer: Customer, room_number: int, nights: int) -> bool:
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

        if customer.pay_for_booking(total_price):
            selected_room.book_room()
            customer.add_room(selected_room)
            self.log_booking(customer, selected_room, total_price)
            return True
        else:
            logging.warning(f"დაჯავშნა ჩაიშალა: კლიენტს {customer.name} არ აქვს საკმარისი ბიუჯეტი ({total_price}₾ სჭირდება).")
            return False

    # ჯავშნის გაუქმება, ოთახის გათავისუფლება სიიდან ამოღება, დალოგვა
    def cancel_booking(self, customer: Customer, room_number: int) -> bool:
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


# ---ტერმინალი
if __name__ == "__main__":
    print("=== სასტუმროს სისტემის სიმულაციის დაწყება ===")
    
    # სასტუმროს და ოთახების შექმნა
    my_hotel = Hotel("mariott")
    my_hotel.add_room(Room(101, "Single", 150.0, 1))
    my_hotel.add_room(Room(102, "Double", 200.0, 2))
    my_hotel.add_room(Room(103, "Suite", 300.0, 4))
    
    # მომხმარებლის შექმნა
    guest = Customer("შოთა", 500.0)
    
    print("\n1. თავისუფალი ოთახების ჩვენება:")
    for room in my_hotel.show_available_rooms():
        print(room)
        
    print("\n2. შოთა ცდილობს დაჯავშნოს 102 ოთახი 3 ღამით (ფასი: 540₾, ბიუჯეტი: 500₾):")
    my_hotel.book_room_for_customer(guest, 102, 3)
    
    print("\n3. შოთა ჯავშნის 101 ოთახს 5 ღამით (ფასი: 500₾, ფასდაკლებით: 450₾):")
    my_hotel.book_room_for_customer(guest, 101, 5)
    
    print("\n4. მომხმარებლის სტატუსი დაჯავშნის შემდეგ:")
    print(guest.show_booking_summary())
    
    print("\n5. ოთახის გაუქმების ტესტირება:")
    my_hotel.cancel_booking(guest, 101)
    print(guest.show_booking_summary())