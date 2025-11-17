def fuel_model():
    print("Before the ride questionnaire")
    age = input("Enter your age: ")
    sex = input("Enter your sex: ")
    weight = input("Enter your weight: ")
    height = input("Enter your height: ")
    rider = f"Your age is {age}, your sex is {sex}, your weight is {weight}, your height is {height}"
    print(rider)
    
    print("Let's go on a hypothetical ride")
    distance = input("Enter the distance of the ride: ")
    elevation_gain = input("Enter the elevation gain of the ride: ")
    ride_time = input("Enter the ride time in minutes: ")
    ride = f"The distance of the ride is {distance}, the elevation gain is {elevation_gain}, the ride time is {ride_time} minutes"
    print(ride)
    
    model_result = []

    fake_noticiation_1 = f"Timestamp: 00:20, kcal: 100"
    fake_noticiation_2 = f"Timestamp: 00:30, kcal: 50"
    fake_noticiation_3 = f"Timestamp: 00:50, kcal: 150"
    fake_noticiation_4 = f"Timestamp: 01:10, kcal: 80"
    fake_noticiation_5 = f"Timestamp: 01:30, kcal: 180"
    fake_noticiation_6 = f"Timestamp: 01:50, kcal: 100"
    fake_noticiation_7 = f"Timestamp: 02:10, kcal: 50"
    fake_noticiation_8 = f"Timestamp: 02:30, kcal: 120"
    fake_noticiation_9 = f"Timestamp: 02:40, kcal: 100"
    fake_noticiation_10 = f"Timestamp: 03:00, kcal: 50"

    model_result.append(fake_noticiation_1)
    model_result.append(fake_noticiation_2)
    model_result.append(fake_noticiation_3)
    model_result.append(fake_noticiation_4)
    model_result.append(fake_noticiation_5)
    model_result.append(fake_noticiation_6)
    model_result.append(fake_noticiation_7)
    model_result.append(fake_noticiation_8)
    model_result.append(fake_noticiation_9)
    model_result.append(fake_noticiation_10)

    return model_result