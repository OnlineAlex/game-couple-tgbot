import os

TOKEN = os.environ['TELEGRAM_TOKEN']
DB_FILENAME = 'GamesData.db'

levels = {
    'Простой :chicken:': 16,
    'Средний :monkey:': 24,
    'Сложный :person_lifting_weights:': 36
}

top_ratings = {
    16: 'top_easy_rating',
    24: 'top_normal_rating',
    36: 'top_hard_rating'
}

game_emj = [
    ':detective:', ':grinning_face_with_smiling_eyes:',
    ':smiling_face_with_heart-eyes:', ':face_screaming_in_fear:',
    ':sunglasses:', ':face_with_tears_of_joy:', ':face_with_medical_mask:',
    ':smiling_face_with_horns:', ':boy:', ':people_with_bunny_ears:',
    ':alien:', ':woman:', ':baby_angel:', ':weary_cat_face:',
    ':guard:', ':ghost:', ':Santa_Claus:', ':family:', ':see-no-evil_monkey:'
]

