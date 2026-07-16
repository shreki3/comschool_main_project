import unittest
from hotel_system import Room, Customer, Hotel

class TestHotelSystem(unittest.TestCase):

    def setUp(self):
        # სატესტო გარემოს მომზადება ყოველი ტესტის წინ
        self.hotel = Hotel("გრანდ ბუდაპეშტი")
        
        self.room1 = Room(room_number=101, room_type="Single", price_per_night=100.0, max_guests=1)
        self.room2 = Room(room_number=102, room_type="Double", price_per_night=180.0, max_guests=2)
        
        self.hotel.add_room(self.room1)
        self.hotel.add_room(self.room2)
        
        self.customer = Customer(name="შოთა", budget=500.0)

    # 1. ტესტი Customer.pay_for_booking() - ბიუჯეტის სწორად შემცირება
    def test_pay_for_booking_success(self):
        initial_budget = self.customer.budget
        payment_amount = 200.0
        
        # გადახდა უნდა განხორციელდეს წარმატებით
        success = self.customer.pay_for_booking(payment_amount)
        self.assertTrue(success)
        
        # ბიუჯეტი სწორად უნდა შემცირდეს
        self.assertEqual(self.customer.budget, initial_budget - payment_amount)
        
        # ქულები სწორად უნდა დაერიცხოს (200 / 10 = 20 ქულა)
        self.assertEqual(self.customer.reward_points, 20)

    def test_pay_for_booking_insufficient_funds(self):
        initial_budget = self.customer.budget
        payment_amount = 600.0  # ბიუჯეტზე მეტია
        
        # გადახდა არ უნდა განხორციელდეს
        success = self.customer.pay_for_booking(payment_amount)
        self.assertFalse(success)
        
        # ბიუჯეტი უცვლელი უნდა დარჩეს
        self.assertEqual(self.customer.budget, initial_budget)

    # 2. ტესტი Hotel.book_room_for_customer() - დაჯავშნა მხოლოდ თავისუფალ ოთახებზე
    def test_book_room_success(self):
        # თავიდან ოთახი თავისუფალია
        self.assertTrue(self.room1.is_available)
        
        # ვჯავშნით 101 ოთახს 2 ღამით (ფასი: 200₾)
        success = self.hotel.book_room_for_customer(self.customer, room_number=101, nights=2)
        
        self.assertTrue(success)
        # ოთახის სტატუსი უნდა გახდეს დაკავებული
        self.assertFalse(self.room1.is_available)
        # მომხმარებლის ბუკინგების სიაში უნდა დაემატოს ოთახი
        self.assertIn(self.room1, self.customer.booked_rooms)

    def test_book_already_booked_room(self):
        # პირველი დაჯავშნა
        self.hotel.book_room_for_customer(self.customer, room_number=101, nights=1)
        
        # მეორე მომხმარებელი ცდილობს იმავე ოთახის დაჯავშნას
        another_customer = Customer(name="ანა", budget=1000.0)
        success = self.hotel.book_room_for_customer(another_customer, room_number=101, nights=1)
        
        # დაჯავშნა უნდა ჩავარდეს, რადგან ოთახი დაკავებულია
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()