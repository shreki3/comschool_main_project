import unittest
from hotel_system import Room, Customer, Hotel

# ტესტების კლასი უნდა აინჰერიტებდეს unittest.TestCase
class TestHotelSystem(unittest.TestCase):

    # ეს მეთოდი ეშვება ავტომატურად ყოველი ინდივიდუალური ტესტ-შემთხვევის წინ.
    def setUp(self):
        self.hotel = Hotel("გრანდ ბუდაპეშტი")
        
        #სატესტო ოთახები
        self.room1 = Room(room_number=101, room_type="Single", price_per_night=100.0, max_guests=1)
        self.room2 = Room(room_number=102, room_type="Double", price_per_night=180.0, max_guests=2)
        
        # ოთახებს ვამატებ სასტუმროში
        self.hotel.add_room(self.room1)
        self.hotel.add_room(self.room2)
        
        #სატესტო მომხმარებელი 500 ლარიანი ბიუჯეტით
        self.customer = Customer(name="შოთა", budget=500.0)


    # ტესტის ფუნქციის სახელი უნდა იწყებოდეს test_
    def test_pay_for_booking_success(self):
        #ბიუჯეტის სწორად შემცირება და ქულების დარიცხვა
        initial_budget = self.customer.budget
        payment_amount = 200.0
        
        #გადახდის მეთოდის გამოძახება
        success = self.customer.pay_for_booking(payment_amount)
        
        #შედეგის შემოწმება
        self.assertTrue(success)
        
        #ბიუჯეტის შემოწმება
        self.assertEqual(self.customer.budget, initial_budget - payment_amount)
        
        #ქულების შემოწმება
        self.assertEqual(self.customer.reward_points, 20)

    def test_pay_for_booking_insufficient_funds(self):
        #გადახდის წარუმატებლობა. მომხმარებელს არ აქვს საკმარისი თანხა
        initial_budget = self.customer.budget
        payment_amount = 600.0
        

        success = self.customer.pay_for_booking(payment_amount)
        
        # უნდა დაბრუნდეს False ანუ ვერ გადავიხადეთ
        self.assertFalse(success)
        
        # ბ) ბიუჯეტი არ იცვლება რაადგან ვერ გადავიხადეთ
        self.assertEqual(self.customer.budget, initial_budget)



    def test_book_room_success(self):
        #ოთახის დაჯავშნა ანუ თავისუფალია და ფული გვყოფნის
        #ოთახი ცარიელია
        self.assertTrue(self.room1.is_available)
        
        #  101 ოთახი 2 ღამით საკმარისი თანცა გვაქ
        success = self.hotel.book_room_for_customer(self.customer, room_number=101, nights=2)
        self.assertTrue(success)
        
        #ოთახის სტატუსი გახდა დაკავებული
        self.assertFalse(self.room1.is_available)
        
        #ოთახი უნდა ჩანდეს იუზერის ოთახების სიაში
        self.assertIn(self.room1, self.customer.booked_rooms)

    def test_book_already_booked_room(self):
        #თუ ოთახი უკვე დაიკავა სხვამ, ვერ ვჯავშნით.
        # პირველი წარმატებით ჯავშნის 101 ოთახს 1 ღამით
        self.hotel.book_room_for_customer(self.customer, room_number=101, nights=1)
        
        #მეორე მომხმარებელი დიდი ბიუჯეტით
        another_customer = Customer(name="ჯოტია", budget=1000.0)
        
        # ჯოტია ცდილობს დაჯავშნოს ჩემი ოთახი
        success = self.hotel.book_room_for_customer(another_customer, room_number=101, nights=1)
        
        #უნდა დაბრუნდეს ფოლსი
        self.assertFalse(success)

#ვუშვებ ტერმინალიდან და მუშაობს
if __name__ == "__main__":
    unittest.main()