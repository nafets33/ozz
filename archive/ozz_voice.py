import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', 3)

rate = engine.getProperty('rate')
# engine.setProperty('voice', 'com.apple.speech.synthesis.voice.samantha')

# engine.setProperty('voice', 'english+f3')
engine.setProperty('rate', 170)
text = "I love my family, my wonderful girls"
text = """
Once upon a moonlit night in a dense forest, there lived a small and timid mouse named Milo. Milo was known far and wide as the cleverest mouse in the entire forest, but he had a problem. You see, Milo was not only clever, but he was also very curious. This curiosity often led him into trouble, and on this particular night, he found himself in a rather perilous situation.
Milo had heard stories of a wise and mysterious owl named Olivia, who resided high up in the tallest tree in the forest. The other animals whispered that Olivia possessed knowledge of the world beyond the forest, and Milo's curiosity got the better of him. He decided to climb up to Olivia's tree to ask her about the world outside.
As he made his way up the towering tree, Milo's heart raced with anticipation and a touch of fear. When he finally reached the top, he found Olivia perched gracefully on a branch, her large, golden eyes gleaming in the moonlight.
"Who dares to disturb my solitude?" hooted Olivia, her voice echoing through the forest.
Milo, though trembling with fear, spoke up, "It's me, Milo, the mouse. I've come to seek your wisdom, dear owl."
Olivia, with a bemused look, leaned closer to inspect the little mouse. She could have easily made a meal out of him, but there was something about his determination that intrigued her. "What wisdom do you seek, little one?"
Milo explained his burning desire to know about the world beyond the forest, the oceans, and the mountains. He had heard that Olivia had seen these wonders and hoped she could share her knowledge.
Olivia, initially tempted to eat the mouse, found herself touched by his innocent curiosity. Instead of making a meal out of Milo, she decided to show him the world herself.
So, Olivia and Milo embarked on an incredible adventure. They soared high above the forest, and Milo marveled at the vastness of the world. He saw sparkling oceans, towering mountains, and endless landscapes. Along the way, Olivia shared stories of her travels and the wonders she had seen.
As the days turned into weeks, Olivia and Milo's friendship grew stronger. They encountered thunderstorms, crossed deserts, and explored dense jungles. Olivia realized that she no longer desired to eat Milo but instead cherished their companionship.
One day, as they watched a breathtaking sunset over a serene lake, Olivia turned to Milo and said, "Milo, I must confess something. When you first climbed up to my tree, I had intended to eat you. But your curiosity and bravery have changed my heart. You are a dear friend, and I am grateful for our adventures together."
Milo smiled warmly at Olivia, "And you, dear Olivia, have shown me a world I could only dream of. You are not only wise but kind-hearted, and I am grateful for your friendship as well."
From that moment on, Olivia and Milo were inseparable. They continued their journey, exploring the world together, and their friendship blossomed into something truly magical. They met creatures from all corners of the Earth, and wherever they went, their unique bond inspired others to put aside their differences and build friendships.
Olivia, the once-mighty owl, and Milo, the clever mouse, had shown the world that even the most unexpected friendships could be the most beautiful. They traveled the world as best friends, spreading the message that kindness and curiosity could bridge any divide and bring the most wonderful adventures to life.
"""
engine.say(text)
# engine.say('I love my family, I love my girls')
# engine.runAndWait()

# for voice in voices:
#    print(voice.id)
#    engine.setProperty('voice', voice.id)
#    engine.setProperty('rate', 150)
#    engine.say(text)
# #    engine.say('The quick brown fox jumped over the lazy dog.')

engine.runAndWait()