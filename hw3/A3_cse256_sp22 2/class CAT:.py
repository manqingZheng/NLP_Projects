class CAT:
    def __init__(self, age=1, gender='female') -> None:
        self.age = age
        self.gender = gender


latiao = CAT(gender='male')
latiao.age = 3

# def generate_a_cat(age=100, gender='non'):
#     latiao = CAT(age, gender)
#     return latiao

# latiao = generate_a_cat()

print(latiao.age, latiao.gender)
