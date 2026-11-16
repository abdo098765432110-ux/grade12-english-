# -*- coding: utf-8 -*-
"""«حل 25 قطعة» — reading passages by Mr. Ahmed Tarek (م. عبقري لغة), Grade 12 English.

Source: the teacher's PDF (29 pages). The file has 26 passages: two of them are numbered 10.
Only obvious typing mistakes in the PDF were corrected (listed in FIXES below); a few prompts that
pointed at an "underlined" word now quote the phrase, because the PDF shows no underlining.
The answers and explanations were worked out from the passages (not from an answer key).

Each question: (prompt, [options], correct letter, explanation in Egyptian Arabic with the evidence).
Run: python3 tools/reading_25/build.py
"""

TEACHER = "م. عبقري لغة"
SOURCE = "م. عبقري لغة — ملزمة «حل 25 قطعة»"

# Passage numbers as on the site (the same as in the PDF; its two passages numbered 10 are 10 (a) and 10 (b)).
FIXES = [
    "P1: 'more 20 cities' → 'more than 20 cities'; 'heat of the Perhaps' → 'heat of the sun. Perhaps'; 'even the land isn't desert' → 'even the land that isn't desert'.",
    "P2 Q7: option c 'as good as' → 'as warm as'; the unclear option d ('not too cold as your body temperature') → 'colder than your body temperature'.",
    "P3: the first paragraph split in two (reasons / the website); Q6 prompt was a repeat of Q7 ('What is the purpose of the article?').",
    "P4: 'on us we grow' → 'on us as we grow'; 'their own lies' → 'their own lives'.",
    "P7: a repeated phrase removed ('they may fail at times'); 'There can interfere' → 'These can interfere'; split into paragraphs.",
    "P9: the broken sentence 'Biochemist.' completed (Bertram Collip purified the insulin), as the questions ask about him; 'Frederic' → 'Frederick'.",
    "P10 (b): 're generalists' → 'are generalists'; 'blackfish spots and strips' → 'blackish spots and stripes'.",
    "P13: the missing sentence about carbohydrates (bread, potatoes and rice) restored, as question 3 asks about it; the broken sentence about the tin of soft drink rewritten.",
    "P14: broken sentences in the last paragraph made readable (same meaning); option 'discount' → 'discontent'.",
    "P25: '490 B-C-' → '490 BC'; the broken sentence about Olympic athletes made readable.",
    "Small spelling fixes in options: Three, nearest, shining, effective, Frederick, Bertram, use, the shop.",
]

P = []


def passage(paragraphs, questions):
    P.append({"paragraphs": paragraphs, "questions": questions})


# 1 ------------------------------------------------------------------
passage([
    "Many experts believe there are too many people in the world. Unless there are big changes in the way people think about the number of children they should have, the world's population will double in 25 years. There will be more than 20 cities with a population greater than 20 million.",
    "Some people who don't understand what \"over population\" means point to countries such as Australia and say, \"There is plenty of room there.\" Although most of Australia is unpopulated, and much of it is thinly populated, there are reasons for this. Firstly, much of the land is desert and waterless. Secondly, even the land that isn't desert isn't suitable for anything, not even growing grass. Another major problem we shall have to face as the world's population grows is a shortage of energy.",
    "We are using up coal and oil. When they have been used up, we shall have to find something to take their place. It is true that we can make electricity from the heat of the sun. Perhaps the biggest problem we shall have when the world's population doubles will be pollution. The air we breathe is already badly polluted.",
], [
    ("It is expected that the world's population will …… in 25 years.", ["lessen", "decline", "double", "decrease"], "c",
     "الدليل: «the world's population will double in 25 years». يعني هيتضاعف = double. التلاتة التانيين معناهم يقل."),
    ("Australia is relatively a/an …… continent.", ["unpopulated", "populated", "populous", "peopled"], "a",
     "الدليل: «most of Australia is unpopulated». أغلبها مفيهوش سكان، فهي نسبيًا قارة unpopulated."),
    ("The word \"waterless\" in the second paragraph means ……", ["wet", "damp", "fertile", "arid"], "d",
     "كلمة waterless معناها مفيهاش مية، يعني arid (جافة). أما wet وdamp فعكسها، وfertile يعني خصبة."),
    ("The sun's heat can be used to produce ……", ["energy", "grass", "wheat", "crops"], "a",
     "الدليل: «we can make electricity from the heat of the sun». الكهربا طاقة، فالإجابة energy."),
    ("In order to prevent the world's population from being doubled, there must be a change in ……",
     ["the methods of agriculture", "sources of energy they should have", "people's thought about the number of children", "the education of children"], "c",
     "الدليل: «Unless there are big changes in the way people think about the number of children they should have». لازم طريقة تفكير الناس في عدد الأولاد تتغير."),
    ("When coal and oil have been used up, we shall ……",
     ["search for other sources of energy", "use computers instead", "wait for scientists to solve the problem", "try to do without them"], "a",
     "الدليل: «we shall have to find something to take their place». يعني ندوّر على مصادر طاقة تانية."),
    ("…… city / cities will have a population of over 20 million.", ["Two", "Twenty", "Twenty-five", "One"], "b",
     "الدليل: «There will be more than 20 cities with a population greater than 20 million». الرقم المذكور 20 (Twenty). 25 دي عدد السنين مش المدن."),
    ("According to the passage, a great area of Australia is considered …… populated.", ["highly", "densely", "rarely", "extensively"], "c",
     "الدليل: «much of it is thinly populated». thinly = قليل السكان = rarely populated. highly وdensely عكسها."),
])

# 2 ------------------------------------------------------------------
passage([
    "Some doctors think that you should drink a glass of water each morning. You should drink this water first thing, before doing anything else. The temperature of the water should be similar to body temperature; neither too hot nor too cold. Why should you drink this water? Water helps your body in many ways. It helps clean out your kidneys. It prepares your stomach for digestion. Water can also help your intestines work better. After drinking water, the intestines can more easily take out nutrients from our food. Water also helps us go to the bathroom more easily. Scientists suggest that people take in 1,600 milliliters of water each day. But don't drink all of that water in one sitting. If you do, your kidneys will have to work much harder to eliminate it. It's better to drink some in the morning and some in the afternoon. Some people think it's better to drink between meals and not during meals. They think water dilutes the juices produced in our stomachs. This can interfere with normal digestion. Are you drinking enough water every day? Check the colour of your urine. If it is light yellow, you are probably drinking enough. If your urine is very dark yellow, you probably need to drink more water. A little more water each day could make you much healthier.",
], [
    ("What could be the best title for this passage?", ["\"Drink Water, Not Soft Drinks\"", "\"Drink During Meals\"", "\"Drink Between Meals\"", "\"Drink Enough Water\""], "d",
     "القطعة كلها عن شرب المية بكمية كفاية وفوايدها، وبتسأل في الآخر «Are you drinking enough water every day?». الاختيارات التانية تفاصيل أو مش مذكورة."),
    ("Why is it helpful to drink water in the morning?", ["Your kidneys will work harder.", "Your intestines will work well.", "Your juices will be diluted.", "Your urine will be pale yellow."], "b",
     "الدليل: «Water can also help your intestines work better». أما «kidneys will work harder» فده ضرر لو شربت كله مرة واحدة."),
    ("Which of the following is NOT a reason to drink water?", ["So your intestines will work well.", "To get more nutrients.", "To clean out your kidneys.", "To dilute your stomach juices."], "d",
     "تخفيف عصارة المعدة مش فايدة؛ القطعة بتقول إنه ممكن «interfere with normal digestion». التلاتة التانيين فوايد مذكورة."),
    ("Why is it better to drink between meals?", ["So you eat enough food.", "So you don't dilute stomach juices.", "So your urine will not smell bad.", "So you don't overwork your kidneys."], "b",
     "الدليل: «They think water dilutes the juices produced in our stomachs». فبيشربوا بين الوجبات علشان المية ما تخففش العصارة."),
    ("What does urine colour indicate?", ["That you need to eat more food", "That you need to drink more water", "That you need to have enough sleep", "That you need to drink more juice"], "b",
     "الدليل: «If your urine is very dark yellow, you probably need to drink more water»."),
    ("Why shouldn't you drink 1,600 milliliters in one sitting?", ["It will harm your lungs.", "It will harm your kidneys.", "It will make you thirsty.", "It will make you hungry."], "b",
     "الدليل: «your kidneys will have to work much harder to eliminate it». يعني هتتعب الكلى."),
    ("The water you drink should be ……", ["too cold", "too hot", "as warm as your body temperature", "colder than your body temperature"], "c",
     "الدليل: «The temperature of the water should be similar to body temperature; neither too hot nor too cold». (في الملف الاختيار c مكتوب «as good as your body temperature» والمقصود نفس درجة حرارة الجسم، والاختيار d كان مكتوب بشكل مش مفهوم فاتظبط.)"),
    ("The word \"it\" in \"If it is light yellow\" refers to ……", ["your body", "your urine", "your health", "your drinking water"], "b",
     "الجملة اللي قبلها: «Check the colour of your urine. If it is light yellow…». يعني it = your urine. (في الملف مكتوب «underlined» من غير خط، فحددنا الكلمة.)"),
])

# 3 ------------------------------------------------------------------
passage([
    "Every time you're online, you are bombarded by pictures, articles, and links trying to tell their story. Unfortunately, not all of these stories are true. Sometimes they want you to click on another advertisement at their own site, other times they want to upset people for political reasons, and the result is … fake news. Read these tips, and don't get fooled!",
    "Look at the website where the story comes from. Does it look real? Is the text well written? Are there a variety of other stories or is it just one story? Fake news websites often don't have many real stories about other topics. If you aren't sure, click on the 'About' page and look for a clear description of the organization.",
    "Many fake news stories use images that are photoshopped or taken from an unrelated site. Sometimes, if you just look closely at an image, you can see if it has been changed. Or use a tool like Google Reverse Image search. It will show you if the same image has been used in other contexts.",
    "Look to see if the story you are reading is on other news sites that you know and trust. If you do find it on many other sites, then it probably isn't fake. There are other techniques that fake news uses. These include using ALL CAPS and lots of ads that pop up when you click on a link. Also, think about how the story makes you feel. If you find a news story that you know is fake, the most important advice is: don't share it!",
], [
    ("The best title for the text is ……", ["Experts show dangers of fake news", "Experts share top tips for resisting fake news", "How to create fake news: a guide", "Tips on how to read the news online"], "b",
     "القطعة بتقول «Read these tips, and don't get fooled!» وبعدها نصايح علشان ما تتخدعش بالأخبار الكاذبة = tips for resisting fake news."),
    ("Which reason is NOT given for an online fake news story?", ["To convince people of a political view", "To make people angry or sad", "To plant a virus in your computer", "To click on an advertisement"], "c",
     "الأسباب المذكورة: الإعلانات «click on another advertisement» وإزعاج الناس لأسباب سياسية «upset people for political reasons». الفيروسات مش مذكورة."),
    ("Which of these may mean that a news site should not be trusted?", ["The site's \"About\" page doesn't clearly describe the organization.", "The text is well written.", "The site has a variety of other stories.", "The site has real stories about other topics."], "a",
     "الدليل: «click on the 'About' page and look for a clear description of the organization». لو مفيش وصف واضح يبقى الموقع مش مضمون. التلاتة التانيين علامات موقع حقيقي."),
    ("The word \"it\" in \"you can see if it has been changed\" refers to ……", ["the story", "the website", "the picture", "the text"], "c",
     "الجملة: «if you just look closely at an image, you can see if it has been changed». it = the image = the picture."),
    ("Which of the following best summarizes the first paragraph?", ["More ways that fake news uses.", "Fake news uses changed photos.", "Reasons for making fake news.", "Fake websites."], "c",
     "الفقرة الأولى بتشرح ليه بيعملوا أخبار كاذبة: الإعلانات وأسباب سياسية. الصور المتعدلة في الفقرة التالتة، والطرق التانية في الأخيرة، والمواقع في التانية."),
    ("If you find a news story that you know is fake, what is the most important advice?", ["Report it to the police.", "Make a note of it for a reference.", "Tell your close friends about it.", "Don't show it to other people online."], "d",
     "الدليل: «the most important advice is: don't share it!» يعني ما توريهاش لحد أونلاين. (في الملف السؤال ده كان مكتوب غلط «What is the purpose of the article?».)"),
    ("What is the purpose of the article?", ["To complain", "To inform", "To entertain", "To blame"], "b",
     "المقال بيدّي معلومات ونصايح للقارئ = to inform. مفيهوش شكوى ولا تسلية ولا لوم."),
    ("The word \"bombarded\" in this text means ……", ["defended", "prevented", "bothered", "covered"], "c",
     "معنى bombarded by pictures إنك بتتهاجم بكمية كبيرة جدًا من الصور لحد ما تتضايق، فأقرب معنى bothered (اتضايق/اتزعج)."),
])

# 4 ------------------------------------------------------------------
passage([
    "People may be divided into two types: winners and losers. Because our families and friends have a great influence on us as we grow, we are born helpless and dependent on our environment. Winners are able to change their situation and become independent by being responsible for their own lives. They don't blame others for their mistakes. They do their own thinking, they listen to others, evaluate what they say, and then they make up their minds. Although they may fail at times, yet they keep self-confidence. Winners overcome their bad experiences. They have enthusiasm for life. They enjoy work, play, food and the world of nature. They freely enjoy themselves but they can postpone it if duty calls.",
    "Losers, on the other hand, never learn to take responsibility for their own lives. There are many causes why people can become losers: disease, poor nutrition, cruelty, unhappy relationships and bad experiences. These can interfere with the normal progress towards becoming a winner. But whereas winners fight these situations, losers hang onto them, and use them as excuses. Losers usually feel anxious, unhappy and bored. They are afraid to try new things and often repeat their own mistakes again and again. When a student fails a mathematics test and then says, \"Oh, well, I've never been good at maths,\" it becomes his excuse for not trying to change this idea, and he remains a loser.",
    "Losers spend their lives waiting for something wonderful to happen to save them from their problems with their lives but never try to change their world themselves. Now, you can decide what people will call you in the future: a loser or a winner.",
], [
    ("What makes us winners or losers from our early life?", ["our teachers", "our environment", "failure", "our friends"], "b",
     "الدليل: «we are born helpless and dependent on our environment». الأصحاب جزء من البيئة، لكن الإجابة الشاملة اللي في القطعة environment."),
    ("Which one of the following doesn't describe winners?", ["They are independent.", "They don't blame others for their mistakes.", "They only follow in others' footsteps.", "They overcome their bad experiences."], "c",
     "الفايزين «do their own thinking… then they make up their minds»، يعني مش بيمشوا ورا غيرهم. التلاتة التانيين صفاتهم في القطعة."),
    ("What do winners do if they fail at times?", ["Keep their self-confidence.", "Lose hope and go out of the race.", "Never try again as it is one chance.", "Ask others to help them."], "a",
     "الدليل: «Although they may fail at times, yet they keep self-confidence»."),
    ("What happens when losers find excuses and don't try to change?", ["Other people help them.", "They find luck and become winners.", "They say that it's fate.", "They remain losers."], "d",
     "الدليل: «it becomes his excuse for not trying to change this idea, and he remains a loser»."),
    ("Which one of the following doesn't describe losers?", ["They are afraid to try new things.", "They are never good at maths.", "They repeat their mistakes again.", "They wait for something good to happen."], "b",
     "جملة «never good at maths» قالها طالب واحد كمثال (عذر)، مش صفة لكل الخسرانين. التلاتة التانيين صفاتهم في القطعة."),
    ("What does the word \"postpone\" mean?", ["stop", "email", "put off", "post"], "c",
     "كلمة postpone معناها يأجّل، يعني put off. «they can postpone it if duty calls» يعني يأجلوا المتعة لو فيه واجب."),
    ("What do winners have for life?", ["Enthusiasm", "Anxiety", "Boredom", "Sadness"], "a",
     "الدليل: «They have enthusiasm for life». القلق والملل صفات الخسرانين."),
    ("What do losers usually feel?", ["Happy", "Anxious", "Interested", "Satisfied"], "b",
     "الدليل: «Losers usually feel anxious, unhappy and bored»."),
])

# 5 ------------------------------------------------------------------
passage([
    "This year I decided to do something to regain my reputation as a kind uncle. My nephew, Ziad, had never forgiven me for the dictionary I had bought him as a birthday present last year. His parents had no reason to be grateful to me either as, the year before, I had presented him with a pot of paste and some funny pictures. Instead of sticking them into a book, Ziad had covered every wall in the house with them. Hence, this year, I decided to let him choose for himself.",
    "We went into a big toyshop but Ziad was highly critical of everything he saw. In vain did I show him toy after toy; he was not to be tempted. Then I saw his eyes light up: he had discovered something he really did approve of: a large tin drum. I was quite pleased until I thought what Ziad's mother would say when she saw it. Nobody would get any sleep for weeks! I led Ziad away quickly, saying that the drum was too expensive.",
    "Ziad asked for permission to go off on his own and I took that chance to sit down and rest my aching feet. Fifteen minutes passed but there was still no sign of Ziad. I began to get worried and began to look for him. I asked a young lady if she had seen a little boy in a grey suit. She pointed out that there were so many little boys in grey suits in the store. I was just beginning to despair, when I saw a strange figure dressed in peculiar purple clothes. The figure was wearing a false beard and had a cave-man's axe in one hand, and a space gun in the other. It was, of course, Ziad, who informed me at once that he was the first cave-man to fly into space.",
], [
    ("The main idea of this passage is how to be a …… uncle.", ["hateful", "loving", "miserable", "serious"], "b",
     "الدليل: «to regain my reputation as a kind uncle». kind قريبة من loving (خال/عم حنين بيحب ابن أخوه)."),
    ("The writer hesitated to buy Ziad the tin drum because it would …… his parents.", ["please", "recognise", "annoy", "blame"], "c",
     "الدليل: «what Ziad's mother would say… Nobody would get any sleep for weeks!» الطبلة هتضايق الأهل = annoy."),
    ("The word \"peculiar\" is an antonym for ……", ["strange", "odd", "mysterious", "familiar"], "d",
     "كلمة peculiar معناها غريب، وعكسها (antonym) familiar يعني مألوف. أما strange وodd فمرادفات مش أضداد."),
    ("The writer bought Ziad a pot of paste to ……", ["cover the walls with pictures", "stick the pictures in a book", "stick the pictures on the cupboard", "stick tickets on his books"], "b",
     "الدليل: «Instead of sticking them into a book, Ziad had covered every wall…». الهدف كان يلزق الصور في كتاب، لكن زياد لزقها على الحيطان."),
    ("The writer thought that …… of the choices Ziad had made would please his parents.", ["the first", "the second", "the third", "nothing"], "d",
     "كل اختيارات زياد كانت هتضايق أهله: الحيطان اتملت صور، والطبلة هتمنعهم من النوم. يعني ولا حاجة = nothing."),
    ("The lady in the shop couldn't tell the writer where Ziad was because ……", ["he had taken off his grey suit", "he had left the shop", "many boys wore clothes similar to his", "she did not see him"], "c",
     "الدليل: «She pointed out that there were so many little boys in grey suits in the store»."),
    ("The writer could hardly recognise Ziad because ……", ["he was disguised", "it was dark", "he carried a space gun", "he seemed much older"], "a",
     "زياد كان لابس هدوم بنفسجي غريبة ودقن صناعية = disguised (متنكر). مسدس الفضاء جزء من التنكر بس مش السبب كله."),
    ("The word \"them\" in \"Instead of sticking them into a book\" refers to ……", ["Ziad's parents", "the walls", "the pictures", "Ziad's parents and uncle"], "c",
     "الجملة اللي قبلها: «a pot of paste and some funny pictures». them = the pictures اللي كان المفروض تتلزق في كتاب."),
])

# 6 ------------------------------------------------------------------
passage([
    "In this tour, we will see some of Egypt's most famous sites. Travelling up the Nile, you will see ancient temples and meet friendly local people. We will visit Cairo, the Pyramids of Giza, Aswan and Luxor. You don't need to book hotels because we will arrange all your accommodation. We will also go camping for a night in the desert, so you need to bring a sleeping bag. It can be cold at night!",
    "You don't have to bring much money because all your food and transport is included in the price. However, you might want to buy some souvenirs from the bazaars that we will visit. You will need to bring cool clothes and good shoes (walking around ancient temples can be difficult). You must also have a passport. Please also check our website for up-to-date information. We know that you'll return with some amazing memories and a happy face!",
    "Egypt is the birthplace of civilization. Egypt is a deep-rooted country. It is famous for eco-tourism and the green environment. So we should be eco-tourists and help the environment. The Nile is the longest river in the world, so we will enjoy a lot of wonderful landscapes and eye-catching places.",
], [
    ("Who is this text written for?", ["It is written for tourists who want to visit Egypt.", "It is written for tourists who want to visit London.", "It is written for tourists who want to visit the River Nile.", "It is written for tourists who want to visit hotels."], "a",
     "إعلان رحلة: «In this tour, we will see some of Egypt's most famous sites» (القاهرة، الأهرامات، أسوان، الأقصر)."),
    ("Why don't people need to take much money with them on this trip?", ["Tourists mustn't buy any souvenirs from the bazaars that we will visit.", "Because people are very poor.", "Because the service is free.", "Because food and transport are included in the price."], "d",
     "الدليل: «all your food and transport is included in the price». الخدمة مش مجانية؛ هي متدفعة في السعر."),
    ("According to the passage, this trip is most suitable for ……", ["very old people", "very young children", "young people", "babies"], "c",
     "الرحلة فيها مشي في المعابد «can be difficult» وتخييم في الصحرا والبرد بالليل، فهي مناسبة للشباب."),
    ("The best title for this passage can be ……", ["The History of Egypt", "A Trip to Egypt", "Tourism in Egypt", "The Nile in Egypt"], "b",
     "القطعة بتوصف رحلة بعينها: الأماكن والإقامة والأكل والحاجات اللي تجيبها معاك = A Trip to Egypt. «Tourism in Egypt» عام زيادة."),
    ("The word \"It\" in \"It can be cold at night!\" refers to ……", ["the desert", "a hotel", "a sleeping bag", "all the accommodation"], "a",
     "الجملة اللي قبلها: «go camping for a night in the desert… It can be cold at night!» يعني الصحرا بالليل بتبقى برد."),
    ("What do you think \"up-to-date\" means?", ["the newest", "very important", "very interesting", "very useful"], "a",
     "معنى up-to-date information أحدث معلومات، يعني the newest."),
    ("I think that the writer of the text is ……", ["telling lies", "telling a story", "telling facts", "telling a novel"], "c",
     "النص معلومات حقيقية عن الرحلة (الأماكن، المطلوب، الباسبور)، مش حكاية ولا رواية = telling facts."),
    ("What does \"eco\" mean in \"It is famous for eco-tourism\"?", ["Related to the environment", "Related to civilization", "Related to pollution", "Related to accommodation"], "a",
     "البادئة eco- معناها له علاقة بالبيئة، والدليل بعدها: «the green environment… help the environment»."),
])

# 7 ------------------------------------------------------------------
passage([
    "Because our families and friends have a great influence on us as we grow up, we are born helpless and dependent on our environment. However, people may be divided into two types: winners and losers.",
    "Winners are able to change their situations and become independent by being responsible for their own lives. They don't blame others for their mistakes. They do their own thinking, listen to others, evaluate what they say, and then make up their minds. Although they may fail at times, yet they keep self-confidence. Winners overcome their bad experiences. They enjoy work, play, food and the world of nature. They freely enjoy themselves but they can postpone it if duty calls.",
    "Losers, on the other hand, never learn to take responsibility for their own lives. There are many causes why people can become losers: disease, poor nutrition, cruelty, unhappy relationships and bad experiences. These can interfere with the normal progress towards becoming a winner. But whereas winners fight these situations, losers hang on to them, and use them as excuses. Losers usually feel anxious, unhappy and bored. They are afraid to try new things and often repeat their own mistakes again and again. Losers spend their lives waiting for something wonderful to happen to save them from their problems with their lives but never try to change.",
    "To sum up, always exert great efforts, be positive and optimistic, but don't be negative or pessimistic. Then, accept and be proud of what you achieve.",
], [
    ("A suitable title of the passage can be ……", ["Family's influence", "Depending on the environment", "How to win", "Winners and losers"], "d",
     "القطعة كلها مقارنة بين نوعين من الناس: «people may be divided into two types: winners and losers»."),
    ("The best summary for the second paragraph is ……", ["winners' efforts", "winners' entertainment", "winners' qualities", "winners' experiences"], "c",
     "الفقرة التانية بتعدّ صفات الفايزين: مستقلين، مش بيلوموا غيرهم، واثقين في نفسهم… = qualities."),
    ("The word \"them\" in \"losers hang on to them\" refers to ……", ["bad situations", "winners", "progresses", "relationships"], "a",
     "الجملة: «whereas winners fight these situations, losers hang on to them». them = these (bad) situations."),
    ("The word \"exert\" can be replaced by ……", ["do", "invent", "make", "give"], "c",
     "معنى exert great efforts يبذل مجهود كبير، يعني make great efforts. التعبير الصح في الإنجليزي make an effort مش do."),
    ("The clause \"winners are able to change their situation\" refers to winners' ……", ["encouragement", "flexibility", "optimism", "dependence"], "b",
     "القدرة على تغيير الموقف = المرونة (flexibility). dependence عكس اللي في القطعة (independent)."),
    ("The writer …… losers for their failure.", ["sympathizes with", "blames", "regrets", "excuses"], "b",
     "الكاتب بيقول إنهم «never learn to take responsibility» و«use them as excuses»، يعني بيحمّلهم المسؤولية = blames."),
    ("Winners ……", ["can delay entertainment if necessary", "are defeated by bad experiences", "enjoy and leave duties behind", "aren't optimistic"], "a",
     "الدليل: «They freely enjoy themselves but they can postpone it if duty calls». postpone = delay."),
    ("Losers are people who ……", ["overcome their bad experiences", "learn to take responsibility", "try to change", "blame others for their mistakes"], "d",
     "الفايزين «don't blame others for their mistakes»، والخسرانين عكسهم وبيستخدموا الظروف «as excuses». التلاتة التانيين صفات الفايزين."),
])

# 8 ------------------------------------------------------------------
passage([
    "Resources are things that we use. Natural resources come from Earth. Many of our natural resources are limited. This means that they will not last forever. Some resources are renewable. This means the resource can be replaced or grown. You can plant a new tree when you cut one down. Other resources are not renewable. This means that they cannot be replaced or grown. You can dig coal out of the ground. Once the coal is used, it is gone. Many of Earth's natural resources are limited, but people can help conserve those resources. When you try to conserve a natural resource, you use less of it, so it does not get used up so fast.",
    "People can conserve fuel, like gasoline, by riding a bicycle or walking. This works well when the distance is short. We needn't drive everywhere. Water is a very important natural resource. We all need it to live. We can conserve water by making sure that our pipes and faucets do not leak. We can also conserve water by making smart choices. One choice is to use the dishwasher and washing machine only when they are full. Another choice is to turn off the water when you brush your teeth. We can all make a difference!",
], [
    ("Resources are things that we ……", ["need", "get", "use", "are available"], "c",
     "أول جملة: «Resources are things that we use»."),
    ("Renewable resources ……", ["may run out", "can be replaced", "can't be replaced", "may not last"], "b",
     "الدليل: «Some resources are renewable. This means the resource can be replaced or grown»."),
    ("We need water to ……", ["save energy", "renew resources", "live", "move"], "c",
     "الدليل: «Water is a very important natural resource. We all need it to live»."),
    ("To save water, use the dishwasher when it is ……", ["connected", "clean", "repaired", "full"], "d",
     "الدليل: «use the dishwasher and washing machine only when they are full»."),
    ("We ride bicycles so that we can ……", ["play games", "save water", "save energy", "make smart choices"], "c",
     "الدليل: «People can conserve fuel, like gasoline, by riding a bicycle». توفير البنزين = توفير طاقة."),
    ("The problem with most of our natural resources is that they will …… one day.", ["move", "change", "last forever", "run out"], "d",
     "الدليل: «Many of our natural resources are limited. This means that they will not last forever» = هتخلص = run out."),
    ("The best title for this article could be ……", ["Saving the Planet", "Wasting Energy", "Saving Resources", "Using Gas"], "c",
     "القطعة عن الموارد الطبيعية وإزاي نحافظ عليها (conserve): البنزين والمية = Saving Resources."),
    ("Individuals …… make a difference in saving energy.", ["can", "can't", "won't", "has to"], "a",
     "آخر جملة: «We can all make a difference!»"),
])

# 9 ------------------------------------------------------------------
passage([
    "There's no doubt that the developments in the medical field have helped a lot of people live longer and happier lives. In the past, a lot of people suffered and even died because of diseases that are now easy to treat thanks to the revolution in the medical field. One hundred years ago, diabetes always killed. A victim of diabetes would often have a damaged body organ called the pancreas, but doctors didn't understand why.",
    "In 1921, a young doctor called Frederick Banting had a theory that the pancreas released a substance that controlled the sugar in the blood. Professor John Macleod at the University of Toronto, Canada, gave him a laboratory, ten dogs, and a medical student called Charles Best as a research assistant. Banting and Best showed that an extract from the pancreas, which they named \"insulin\", could control blood sugar in dogs. Biochemist Bertram Collip then purified the insulin so that it could be used for humans.",
    "The discovery of insulin was a landmark. Diabetic patients no longer died from the disease. Banting and Macleod received the Nobel Prize in Medicine in 1923, but they shared their prize money with Best and Collip.",
], [
    ("The best title for this passage is ……", ["Unknown Scientists", "The Discovery of Insulin", "Diabetes", "The Nobel Prize"], "b",
     "القطعة بتحكي إزاي اتكشف الإنسولين خطوة خطوة، وبتقول «The discovery of insulin was a landmark». السكر وجايزة نوبل تفاصيل."),
    ("Medicine ……", ["will stop one day", "won't develop any more", "is developed every day", "can't be developed"], "c",
     "القطعة بتتكلم عن «the developments in the medical field» و«the revolution in the medical field»، يعني الطب بيتطور باستمرار."),
    ("What role do you think Bertram Collip played?", ["He discovered insulin.", "He provided the laboratory.", "He was a research assistant.", "He made pure insulin for humans."], "d",
     "الدليل: «Biochemist Bertram Collip then purified the insulin so that it could be used for humans». (الجملة دي كانت ناقصة في الملف فاتكملت.) المعمل من ماكلويد، والمساعد بست."),
    ("The word \"a landmark\" can be replaced by a/an ……", ["disadvantage", "advantage", "turning point", "weakness point"], "c",
     "كلمة a landmark هنا معناها حدث غيّر التاريخ، يعني turning point. والدليل بعدها: «Diabetic patients no longer died»."),
    ("According to the passage, diabetes affects the …… badly.", ["lungs", "pancreas", "heart", "stomach"], "b",
     "الدليل: «A victim of diabetes would often have a damaged body organ called the pancreas»."),
    ("Who was the first to realize that the pancreas releases insulin?", ["John Macleod", "Frederick Banting", "Charles Best", "Bertram Collip"], "b",
     "الدليل: «a young doctor called Frederick Banting had a theory that the pancreas released a substance that controlled the sugar»."),
    ("The synonym of the word \"release\" is ……", ["damage", "produce", "avoid", "stop"], "b",
     "في القطعة: «the pancreas released a substance»، يعني البنكرياس أفرز (أنتج) مادة، فـ release هنا معناها produce."),
    ("Who got the Nobel Prize money?", ["One scientist", "Two scientists", "Three scientists", "Four scientists"], "d",
     "بانتنج وماكلويد خدوا الجايزة «but they shared their prize money with Best and Collip» = 4 علماء. ركّز: السؤال عن الفلوس مش الجايزة نفسها (الجايزة لاتنين)."),
])

# 10 -----------------------------------------------------------------
passage([
    "The Chinese invented paper and they were also the first to use paper banknotes for money. Before paper notes were invented in the seventh century, wealthy Chinese traders had used metal coins. These had a hole in the middle so that traders could carry them on pieces of material. But these were very heavy to carry. As a result, traders left the money with someone they trusted. Instead, they carried a piece of paper which said how much money they had. The trader could use this paper note to promise anyone that they could pay for the goods that they wanted to buy.",
    "People in Europe only started to use paper banknotes in the seventeenth century. In England, the king needed money to help fight a war with France. Banks encouraged people to leave money with them and gave handwritten notes saying how much money they had left. The notes said, \"I promise to pay the bearer the sum of…\" and you can still see the same words on English notes today. Bank workers continued to handwrite notes until 1853, when the first notes were printed.",
    "The paper used for banknotes is usually made from a mixture of paper and cotton, and sometimes other materials. Although these other materials make the notes stronger than normal paper, most banknotes only last for about two years. For this reason, some countries tried using plastic notes in 1983. However, the first plastic notes in England were not very successful because the ink came off the notes onto people's hands! Five years later, in 1988, Australia successfully used plastic notes for the first time. Today, many countries use plastic notes, which are stronger than paper notes, last longer and are harder to copy.",
], [
    ("Why did Chinese traders first use notes instead of coins?", ["Because the coins were too heavy to carry.", "Because coins had holes in them.", "Because traders could not trust everyone.", "Because they preferred paper."], "a",
     "الدليل: «But these were very heavy to carry. As a result, traders left the money with someone they trusted. Instead, they carried a piece of paper»."),
    ("Why did banks in England first want people to leave their money with them?", ["The king needed money to fight a war.", "People preferred notes to coins.", "People wanted their money to be safe.", "Banks opened for the first time."], "a",
     "الدليل: «In England, the king needed money to help fight a war with France. Banks encouraged people to leave money with them». (الاختيار في الملف كان مكتوب غلط «to coins».)"),
    ("Why were notes handwritten until 1853?", ["It was cheaper this way.", "It was faster this way.", "There was no technology to print them before this time.", "It was hard to copy the handwriting."], "c",
     "الدليل: «Bank workers continued to handwrite notes until 1853, when the first notes were printed». يعني قبل كده الطباعة ما كانتش موجودة للبنكنوت."),
    ("What is the main idea of the text?", ["Why we use money", "Why we use banks", "The history of paper banknotes", "The history of trade"], "c",
     "القطعة ماشية بالترتيب: الصين في القرن السابع ← أوروبا في القرن السابع عشر ← الطباعة 1853 ← البلاستيك 1983 و1988 = تاريخ البنكنوت."),
    ("The word \"them\" in \"Banks encouraged people to leave money with them\" refers to ……", ["the King's men", "the men in France", "the people who had the money", "the banks"], "d",
     "الناس سابوا فلوسهم مع البنوك: them = the banks."),
    ("What does the word \"bearer\" mean?", ["someone who works in a bank", "a Chinese trader", "someone who carries something", "someone who works for the King"], "c",
     "كلمة bearer معناها اللي شايل (حامل) الورقة، يعني someone who carries something. وجملة «I promise to pay the bearer» معناها: أتعهد أن أدفع لحامل هذا السند."),
    ("Where were paper banknotes first used?", ["In China", "In Europe", "In England", "In Australia"], "a",
     "الدليل: «they (the Chinese) were also the first to use paper banknotes for money»."),
    ("When were paper banknotes first used?", ["In the seventh century", "In the seventeenth century", "In 1988", "In 1983"], "a",
     "الدليل: «Before paper notes were invented in the seventh century». القرن السابع عشر ده أوروبا، و1983 و1988 للبلاستيك."),
])

# 10 (second one in the file) ----------------------------------------
passage([
    "The Nile crocodile is an African crocodile and the second largest extant reptile in the world, after the saltwater crocodile. It lives in different types of aquatic environments such as lakes, rivers and marshlands.",
    "Although it is capable of living in saline environments, this species is rarely found in saltwater, but occasionally inhabits deltas. The Nile crocodile is an opportunistic predator and a very aggressive species of crocodile that is capable of taking almost any animal within its range. Nile crocodiles are generalists, taking a variety of prey. Their diet consists mostly of different species of fish, reptiles, birds and mammals. It has an extremely powerful bite that is unique amongst all animals and sharp conical teeth that sink into flesh, allowing for a grip that is almost impossible to loosen.",
    "Adult Nile crocodiles have a dark bronze colouration above, with faded blackish spots and stripes across the back and a dingy off-yellow on the belly, although mud can often hide the crocodile's actual colour. Their flanks are yellowish-green in colour and have dark patches. Nile crocodiles have green eyes. As they mature, Nile crocodiles become darker.",
    "Nile crocodiles are very social crocodiles. They share basking spots and large food sources such as schools of fish and big carcasses. They also lay eggs to reproduce, which are guarded by the female. They are one of the most dangerous species of crocodile and are responsible for hundreds of deaths of humans every year.",
], [
    ("What is known about Nile crocodiles?", ["They never live in deltas.", "They only live in deltas.", "They no longer live in deltas.", "They sometimes live in deltas."], "d",
     "الدليل: «but occasionally inhabits deltas». occasionally = sometimes."),
    ("Why do Nile crocodiles share schools of fish?", ["Because they are aggressive.", "Because they are deadly.", "Because they are social.", "Because they are conical."], "c",
     "الدليل: «Nile crocodiles are very social crocodiles. They share basking spots and large food sources such as schools of fish»."),
    ("When do Nile crocodiles become darker in colour?", ["When they eat", "When they mature", "When they are hungry", "When they are angry"], "b",
     "الدليل: «As they mature, Nile crocodiles become darker». mature = يكبر/يبلغ."),
    ("Where do you rarely see a Nile crocodile?", ["In lakes", "In rivers", "In deltas", "In saltwater"], "d",
     "الدليل: «this species is rarely found in saltwater». البحيرات والأنهار من أماكن عيشته، والدلتا أحيانًا."),
    ("The word \"Their\" in \"Their diet consists mostly of…\" refers to ……", ["foods", "Nile crocodiles", "prey", "reptiles"], "b",
     "الجملة اللي قبلها: «Nile crocodiles are generalists… Their diet» = أكل تماسيح النيل."),
    ("What is meant by the word \"predator\"?", ["An animal that eats plants.", "An animal that lives in space.", "An animal that lives on land.", "An animal that eats other animals."], "d",
     "كلمة predator معناها حيوان مفترس بيصطاد ويأكل حيوانات تانية، والدليل: «capable of taking almost any animal»."),
    ("…… hides the real colour of Nile crocodiles.", ["Water", "Mud", "Sand", "Spine"], "b",
     "الدليل: «mud can often hide the crocodile's actual colour»."),
    ("The teeth of Nile crocodiles sink into …… allowing for a grip that is almost impossible to loosen.", ["flesh", "flash", "flask", "fuss"], "a",
     "الدليل: «sharp conical teeth that sink into flesh». flesh = لحم. باقي الكلمات شبهها في الشكل بس."),
])

# 11 -----------------------------------------------------------------
passage([
    "Everyone likes to stay fit and healthy, but not everyone succeeds in doing that. Staying healthy is important to ensure a happy life. There are two main tips that people have to follow in order to stay healthy. One of the most helpful ways to stay healthy is to have healthy food and eat it at an appropriate time.",
    "Healthy eating is the cornerstone in protecting our health from many conditions, such as diabetes, heart diseases, cancer and blood pressure. Junk foods should be avoided. Instead of having these fast and unhealthy foods, the diet should contain leafy vegetables, fresh vegetables, fruits, milk and fish. One's diet has a key impact on one's overall health.",
    "Healthy food gives an individual strength and even improves their appearance. Healthy food is good for both an individual's body and skin. Exercising is a physical activity that enhances physical fitness and health. For instance, running and cycling are the important exercises that people should do to ensure keeping the body healthy and fit. Therefore, find some time, about 30 minutes per day, to do exercises. Being healthy is not hard to control: be active and be healthy.",
], [
    ("The main idea of the passage is \"……\".", ["How to exercise", "How to eat healthy food", "How to lead a healthy life", "How to be active"], "c",
     "القطعة فيها نصيحتين: الأكل الصحي والرياضة، والاتنين علشان «stay healthy» = حياة صحية. الاختيارات التانية جزء بس."),
    ("The word \"tips\" in the passage means \"……\".", ["advice", "chance", "game", "opportunity"], "a",
     "كلمة tips معناها نصايح، يعني advice: «two main tips that people have to follow»."),
    ("It's important to eat healthy food at a/an …… time.", ["bad", "suitable", "usual", "unusual"], "b",
     "الدليل: «eat it at an appropriate time». appropriate = suitable (مناسب)."),
    ("According to the passage, …… are the most important exercises for us.", ["swimming and running", "running and cycling", "swimming and cycling", "playing football and cycling"], "b",
     "الدليل: «running and cycling are the important exercises»."),
    ("…… is enough time to do exercises.", ["Half an hour", "A quarter of an hour", "One hour", "Two hours"], "a",
     "الدليل: «about 30 minutes per day». 30 دقيقة = نص ساعة."),
    ("Healthy eating prevents many …… such as diabetes.", ["vegetables", "exercises", "fast foods", "diseases"], "d",
     "الدليل: «many conditions, such as diabetes, heart diseases, cancer and blood pressure» = أمراض."),
    ("Healthy food makes us ……", ["stressed", "weak", "bad", "strong"], "d",
     "الدليل: «Healthy food gives an individual strength»."),
    ("A good diet should contain ……", ["fruits and vegetables", "sweets", "junk food and vegetables", "pizza"], "a",
     "الدليل: «the diet should contain leafy vegetables, fresh vegetables, fruits, milk and fish». الأكل السريع لازم نتجنبه."),
])

# 12 -----------------------------------------------------------------
passage([
    "While technology is steadily taking control over individual lives, the reading habit is fast vanishing into thin air. TV and the silver screen are filling the minds of modern youth, taking the majority of their free time. We have to think seriously about how the growing generations will find time to read. Video and television are responsible for the declining interest in reading among youth. They do nothing to build up reading skills. If children's time were devoted to reading, the population would be better educated.",
    "Reading a story is an active partnership between a writer and a reader. Ideas are sketched and the mind of the reader creates the rest, but watching something is totally passive. The problem is that many children read very slowly. It is hardly surprising that such children declare that they find reading boring and prefer to watch television. Their difficulty is not reading the words – it is interpreting them. They need to be able to read fast enough to feed the mind's hunger for a story. Only by reading daily will a child become a strong and independent reader. Parents need to be convinced of the importance of preventing their children from wasting their time. Without their television, the child is likely to turn to books for entertainment.",
], [
    ("The best title for the passage is \"……\".", ["The Importance of Reading", "Children's Preferences", "The Benefits of Technology", "Technology Pros"], "a",
     "الكاتب بيدافع عن القراية: بتعلّم وتخلي الطفل قارئ قوي، والتلفزيون سلبي. يعني أهمية القراءة."),
    ("There is a fruitful partnership between a writer and a reader when ……", ["a video is watched", "a book story is read", "an article is published", "a short story is read"], "b",
     "الدليل: «Reading a story is an active partnership between a writer and a reader»، مقارنة بالفيديو اللي «totally passive». وفي الآخر الطفل بيرجع للكتب «turn to books». أما d فبتقول «short»، والقطعة ما قالتش إن القصة قصيرة."),
    ("What is the reason behind the decline in the reading habit among youth?", ["Lack of free time.", "TV and video.", "Doing sports.", "Not going to school."], "b",
     "الدليل: «Video and television are responsible for the declining interest in reading among youth»."),
    ("The synonym of the word \"independent\" is ……", ["self-centered", "self-determining", "active", "intelligent"], "b",
     "كلمة independent معناها مستقل بيعتمد على نفسه، يعني self-determining. أما self-centered فمعناها أناني، معنى تاني خالص."),
    ("According to the writer's view, TV is …… means of entertainment.", ["not an effective", "not a cheap", "an effective", "an encouraging"], "a",
     "الكاتب شايف التلفزيون «totally passive» و«do nothing to build up reading skills»، يعني مش وسيلة مفيدة. (في الملف الاختيار c مكتوب «an affective».)"),
    ("The pronoun \"They\" in \"They do nothing to build up reading skills\" refers to ……", ["the youth", "reading skills", "children", "video and television"], "d",
     "الجملة اللي قبلها: «Video and television are responsible… They do nothing to build up reading skills»."),
    ("Reading helps people to be ……", ["well-paid", "good writers", "well-educated", "good actors"], "c",
     "الدليل: «If children's time were devoted to reading, the population would be better educated»."),
    ("Children who read slowly ……", ["like TV", "are disabled", "like reading", "speak fast"], "a",
     "الدليل: «such children declare that they find reading boring and prefer to watch television»."),
])

# 13 -----------------------------------------------------------------
passage([
    "The human body is like a machine that is moving and working all the time. All machines need fuel to give them energy. The fuel for the human body is food, and most of the energy comes from two substances in our food: carbohydrates and fats. Carbohydrates come from food like bread, potatoes and rice. Fats come from food like cheese, butter, oil and meat.",
    "Energy in food is measured in calories. For example, an apple has about 40 calories, an egg has about 80, a fresh date has 15, and a tomato has around 12. Carbohydrates and fats have a lot of calories. For instance, a tin of soft drink, which contains a lot of sugar, has 145, a piece of bread has 165, and only one spoonful of cooking oil has 120 calories. You need about 40 calories a day for each kilo that you weigh. So, if you weigh 60 kilos, you will need about 2400 calories per day. If a person eats all the calories he or she needs in his or her meals, but in addition drinks only one tin of soft drink a day, he or she may gain five kilos per year.",
    "Unfortunately, food which contains carbohydrates is usually cheaper than other food, and it is often convenient and attractive. All 'junk food' contains lots of carbohydrates and fats. If your diet contains a lot of junk food, you will probably get fat.",
], [
    ("What is the best title for the passage?", ["How to Become Healthy", "How to Get Energy", "Fats and Carbohydrates"], "c",
     "الكربوهيدرات والدهون في كل فقرات القطعة: هما مصدر الطاقة، وفيهم سعرات كتير، والأكل السريع مليان بيهم فيتخن. «How to Get Energy» بيغطي أول فقرة بس."),
    ("How many calories do tins of soft drink have?", ["A small number", "A few", "None", "Many"], "d",
     "الدليل: «a tin of soft drink, which contains a lot of sugar, has 145». ودي من الحاجات اللي «have a lot of calories»."),
    ("We find carbohydrates in ……", ["bread, potatoes and rice", "cheese, butter, oil and meat", "oranges and mangoes", "vegetables and fruits"], "a",
     "الدليل: «Carbohydrates come from food like bread, potatoes and rice». الجبنة والزبدة والزيت واللحمة = دهون. (الجملة دي كانت ناقصة في الملف فاتكملت.)"),
    ("\"All 'junk food' contains lots of carbohydrates and fats. If your diet contains a lot of junk food, you will probably get fat.\" This means that junk food is ……", ["healthy", "poisonous", "unhealthy", "necessary"], "c",
     "أكل بيخلي الإنسان يتخن = مش صحي = unhealthy. poisonous (سام) مبالغة مش في القطعة."),
    ("What do cheese, butter and oil contain?", ["Fats", "Carbohydrates", "Salts", "Vitamins"], "a",
     "الدليل: «Fats come from food like cheese, butter, oil and meat»."),
    ("Where does energy for the human body come from?", ["Junk food", "Carbohydrates and fats", "Protein and foods", "Soft drinks"], "b",
     "الدليل: «most of the energy comes from two substances in our food: carbohydrates and fats»."),
    ("How many calories does a person who weighs 40 kilos need a day?", ["2000 calories", "165 calories", "1600 calories", "2400 calories"], "c",
     "القاعدة: «about 40 calories a day for each kilo». 40 كيلو × 40 = 1600 سعر. (2400 دي للي وزنه 60 كيلو.)"),
    ("Which statement is true?", ["Food which contains carbohydrates doesn't make us fat.", "Food which contains carbohydrates has fewer calories.", "Food which contains carbohydrates isn't expensive and is well liked.", "Food which contains carbohydrates is the only food useful for the body."], "c",
     "الدليل: «food which contains carbohydrates is usually cheaper than other food, and it is often convenient and attractive»."),
])

# 14 -----------------------------------------------------------------
passage([
    "\"A friend in need is a friend indeed.\" Has that wise saying been proved to you? Did any of your close friends ever stand beside you at the times of sorrow and distress or at the times of joy? That has become like a needle in a haystack in these times of struggling and climbing on the shoulders of others.",
    "At the very beginning of one's life, a child makes friends with a lot of peers who may be a mixture of good and bad. Due to his young age, he can't perfectly judge or decide with whom to keep or lose friendship. By the time he becomes older, the number of friends decreases to a number that doesn't exceed the fingers of one hand. It all depends on to what extent they are faithful, selfless and honest to each other.",
    "Friendship, which all mankind always searches for, as it is mainly a human instinct and man is social by nature, has become a rare value. Friends can help you celebrate good times, protect you from loneliness and give you a sense of belonging. The so-called \"friends\" on social media, who only contact you through comments or emojis to congratulate or condole instead of hurrying to stand right next to you when you are in tough conditions, are false friends. My advice is to choose your friends carefully.",
], [
    ("\"Climbing on the shoulders of others\" – this expression describes ……", ["true friends", "selfish friends", "friends on social media", "brave friends"], "b",
     "اللي «بيطلع على كتاف غيره» بيستغل الناس علشان مصلحته = أناني selfish، عكس الصديق الحقيقي اللي «selfless»."),
    ("The word \"decrease\" in the second paragraph is an antonym of ……", ["expand", "decline", "contract", "shrink"], "a",
     "كلمة decrease معناها يقل، وعكسها expand يعني يزيد ويتسع. أما decline وcontract وshrink فكلهم مرادفات (يقل/ينكمش)."),
    ("Man always needs friends because ……", ["he has much free time", "he needs to laugh at others", "he is greedy by nature", "this is how he was created"], "d",
     "الدليل: «it is mainly a human instinct and man is social by nature» = الإنسان اتخلق كده (غريزة)."),
    ("The writer thinks that true friendship has become ……", ["common", "widely spread", "uncommon", "hateful"], "c",
     "الدليل: «has become a rare value» و«a needle in a haystack». rare = uncommon."),
    ("What do you think \"emojis\" are?", ["Games for entertainment", "Computer devices", "Figures and symbols", "Tools and equipment"], "c",
     "الـ emojis هي الوشوش والرموز الصغيرة اللي بنبعتها في الكومنتات والرسايل، يعني figures and symbols."),
    ("\"Close\" in the first paragraph has the same meaning as ……", ["locked", "best", "hateful", "opponent"], "b",
     "معنى close friends أصحاب مقربين، يعني best friends. أما locked فده معنى close التاني (مقفول) ومش المقصود هنا."),
    ("Friendship protects us from feelings of ……", ["loneliness and discontent", "relief and relaxation", "fear and horror", "calmness and excitement"], "a",
     "الدليل: «Friends can… protect you from loneliness and give you a sense of belonging». الصحاب بيبعدوا عننا الوحدة وعدم الرضا. (في الملف مكتوب «discount» بدل discontent.)"),
    ("The writer advised us to ……", ["text our friends at times of sorrow", "decrease the number of our friends", "select our friends correctly", "use social media correctly"], "c",
     "آخر جملة: «My advice is to choose your friends carefully»."),
])

# 15 -----------------------------------------------------------------
passage([
    "Should we work all the time without having any rest or entertainment? The answer is that we cannot go on working without stopping, from time to time and at regular intervals, to have some rest and recreation. If we do so, we can make mistakes and the quality of our work might get worse.",
    "An overworked person may end up losing the ability to think clearly and having no energy to go on working. Sleep is one of the ways in which nature renews our energy.",
    "Sports and games are also essential for brain workers who stay in closed offices and do not have a good chance to exercise their muscles. Such activities as swimming and walking may do a lot of good to them. So, we should not waste our weekends. They should be made full use of and spent in the open. Having forgotten all about our work and the worries of life, we can then enjoy ourselves to the full and return the next day to work with our energy fully renewed. Change has a magic effect on a man's health and consequently on his performance.",
], [
    ("The best summary of the passage is ……", ["We don't have time for entertainment.", "Work hard all the time.", "Man should have time for entertainment.", "Entertainment is a waste of time."], "c",
     "الفكرة: «we cannot go on working without stopping… to have some rest and recreation» = لازم وقت للراحة والترفيه."),
    ("Overworking results in ……", ["creative thinking", "more experience", "loss of energy", "more energy"], "c",
     "الدليل: «An overworked person may end up… having no energy to go on working»."),
    ("The writer suggests that brain workers …… in the open.", ["should waste their weekends", "should spend their weekends", "should give up their weekends", "shouldn't spend their weekends"], "b",
     "الدليل: «we should not waste our weekends. They should be made full use of and spent in the open»."),
    ("\"Change has a magic effect on man's health.\" The word \"magic\" in the sentence means ……", ["bad", "passive", "negative", "positive"], "d",
     "معنى magic effect هنا تأثير جميل وقوي ومفيد، يعني positive، لأنه بيجدد طاقتنا ويحسّن الأداء."),
    ("The word \"intervals\" can have the meaning of ……", ["periods", "classes", "starts", "lessons"], "a",
     "معنى at regular intervals على فترات منتظمة، فكلمة interval معناها فترة، يعني period."),
    ("Change has a great effect on man's ……", ["chance", "performance", "apology", "taste"], "b",
     "آخر جملة: «Change has a magic effect on a man's health and consequently on his performance»."),
    ("Sports and games are …… for brain workers.", ["harmful", "boring", "essential", "not important"], "c",
     "الدليل: «Sports and games are also essential for brain workers»."),
])

# 16 -----------------------------------------------------------------
passage([
    "Octopuses are extremely intelligent. They have even learnt a few tricks to get them out of sticky situations. For example, when they are afraid of a predator, as octopuses don't have teeth or sharp claws to defend themselves, they hide in the sand on the bottom of the ocean floor. The octopus is like a chameleon because it can change the colour of its skin to match the sand. Some octopuses like to stay in more shallow water where there are rocks and coral.",
    "However, octopuses can squeeze themselves into small spaces between the rocks to get out of reach of predators. Another way an octopus can use to hide is by shooting ink. An octopus uses a part of its body called a siphon to shoot ink into the water. The ink forms a cloud that hides the octopus. It's like a magician doing a vanishing act. If an octopus is attacked, it can actually make itself look like a venomous sea snake. It will bury itself in the sand, keeping two arms visible. If an octopus is in trouble, it can break off one of its arms. The arm will then change colours and squirm around in the water to distract the predator while the octopus swims away to safety. Amazingly, the octopus's arm will grow back.",
], [
    ("A …… is an animal that attacks and kills octopuses.", ["prey", "predator", "chameleon", "magician"], "b",
     "كلمة predator معناها الحيوان المفترس اللي بيهاجم. أما prey فمعناها الفريسة (يعني الأخطبوط نفسه هنا)."),
    ("When an octopus is in a sticky situation, it means it's ……", ["easy", "in danger", "covered in sticks", "unable to move"], "b",
     "معنى sticky situation موقف صعب أو خطر، والدليل الأمثلة بعدها: «when they are afraid of a predator»."),
    ("The synonym of the word \"intelligent\" is ……", ["smart", "dangerous", "venomous", "visible"], "a",
     "كلمة intelligent معناها ذكي، يعني smart."),
    ("The octopus and the chameleon are similar as both ……", ["swim in the same way", "eat the same food", "catch small fish", "can change their skin colour"], "d",
     "الدليل: «The octopus is like a chameleon because it can change the colour of its skin»."),
    ("The best title for this passage is ……", ["The Magician Octopuses", "The Sea World and the Predator", "The Seabed", "The Sea Ink"], "a",
     "القطعة عن حيل الأخطبوط الذكية للهروب، وبتشبهه بالساحر «like a magician doing a vanishing act». الحبر حيلة واحدة بس."),
    ("The octopus can shoot ink into the water, which ……", ["kills the attackers", "helps it hide from the attackers", "pollutes the water", "attracts prey"], "b",
     "الدليل: «The ink forms a cloud that hides the octopus»."),
    ("Octopuses don't have teeth or sharp claws to defend themselves; ……", ["so, they are eaten easily", "however, they have other ways to keep enemies away", "moreover, they are not brave", "that's why they are about to become extinct"], "b",
     "القطعة كلها حيل تانية للدفاع: الاستخبى في الرمل، تغيير اللون، الحبر، تقليد الثعبان، فصل الدراع. يعني however عندهم طرق تانية."),
])

# 17 -----------------------------------------------------------------
passage([
    "Trees are beautiful. They are the useful gifts of nature. They are great friends of man. They give us flowers, fruits, timber, bamboo and fuel. We can rest in the cool shade of a tree. We get wood from the trees to make furniture, doors and windows. Trees are also a great source of rainfall. Trees prevent soil erosion. They protect us from severe weather. Trees are part and parcel of earthly life. All life, directly or indirectly, owes its existence to them. Trees release oxygen, which we need for our life. They also absorb carbon dioxide gas. Many living species live in trees. Trees form natural habitats for many animals, birds and insects. Trees help make the land fertile. We get good crops from fertile land.",
    "They are the source of fruits and flowers. They offer us cool shade during summer. During the rainy season, we take shelter under trees. Trees and plants are the source of many life-saving drugs. They prevent land erosion and guard us against pollution. Thus, trees keep up the ecological balance. Trees protect us from inclement wind, too. Seeds, nuts and fruits are food sources for humans and animals. Trees protect the biodiversity of the ecosystem. Tree resins are used in producing varnishes. Essential oils derived from trees are used in the medical and aroma industries. Thus, trees play an important role in our life. Cutting down trees disturbs the ecosystem. We should preserve trees and plants with great care.",
], [
    ("All life …… its existence to trees.", ["awes", "lays", "owes", "owns"], "c",
     "الدليل: «All life… owes its existence to them». owe = مدين بـ. باقي الكلمات شبهها في الشكل."),
    ("Doors, windows and …… are made of wood.", ["silver", "gold", "furniture", "cars"], "c",
     "الدليل: «We get wood from the trees to make furniture, doors and windows»."),
    ("Cutting down trees …… the ecosystem.", ["causes", "disturbs", "encourages", "freshens"], "b",
     "الدليل: «Cutting down trees disturbs the ecosystem»."),
    ("Many birds, animals and …… take trees as natural habitats.", ["seeds", "plants", "insects", "humans"], "c",
     "الدليل: «Trees form natural habitats for many animals, birds and insects»."),
    ("One needs …… for one's life.", ["oxygen", "nitrogen", "hydrogen", "carbon dioxide"], "a",
     "الدليل: «Trees release oxygen, which we need for our life». ثاني أكسيد الكربون الشجر بيمتصه."),
    ("Trees have …… benefits.", ["a little", "a lot", "little", "many"], "d",
     "القطعة بتعدّ فوايد كتير جدًا. وقواعديًا benefits جمع معدود فنقول many benefits (أما a lot لازم بعدها of)."),
    ("We can rest in the cool …… of a tree.", ["shade", "shake", "shame", "share"], "a",
     "الدليل: «We can rest in the cool shade of a tree». shade = ضِل."),
])

# 18 -----------------------------------------------------------------
passage([
    "Plants have been used for treating illnesses since primitive times. Paintings in the tombs of the pharaohs show that plants were being used by the Ancient Egyptians for medical purposes. Today, some modern drugs are still based on natural herbs. Aspirin, for example, is based on the bark of the willow tree.",
    "Natural remedies are attracting increasing attention all over the world. The advantage of herbal medicine is that the whole of the plant can be used. The powerful substance in the plant cures the illness while the contents of the rest of the plant may help to prevent any harmful side effects. In this way, herbal medicines may be safer than chemical ones. Garlic is just one herb that has been used throughout the world as a cure for diseases, as it is used to treat hair diseases.",
    "Similarly, henna, which is known to be good for the hair, can also be used in the treatment of cancer. If you pay a visit to a herbalist's shop in Cairo, you will be struck by the different colours and smells. There are jars full of tree barks, roots, powders, oils and spices. The customer enters the shop and explains his symptoms to the herbalist, who will take notes, study medical reports and check his reference books before writing out a prescription.",
], [
    ("Natural remedies are attracting attention because they ……", ["are used in Egypt", "have no side effects", "are exported from Egypt", "can treat few diseases"], "b",
     "الدليل: «the rest of the plant may help to prevent any harmful side effects… herbal medicines may be safer than chemical ones». يعني من غير آثار جانبية ضارة."),
    ("Garlic is an example of ……", ["natural remedies", "side effects", "chemical medicines", "modern drugs"], "a",
     "الدليل: «Garlic is just one herb that has been used… as a cure for diseases» = علاج طبيعي."),
    ("…… is a physical condition that shows you may have a particular disease.", ["A prescription", "A symptom", "A remedy", "An ointment"], "b",
     "كلمة symptom معناها عَرَض المرض. أما prescription فهي الروشتة، وremedy العلاج، وointment مرهم."),
    ("A herbalist writes out a prescription …… checking his reference books.", ["while", "during", "after", "before"], "c",
     "الدليل: «check his reference books before writing out a prescription». يعني بيكتب الروشتة بعد ما يراجع الكتب = after."),
    ("The word \"his\" in \"check his reference books\" refers to the ……", ["herbalist", "shop", "customer", "prescription"], "a",
     "الجملة: «the herbalist, who will take notes, study medical reports and check his reference books»، يعني الكتب دي كتب العطار نفسه."),
    ("What is common between garlic and henna? They both ……", ["take care of cancer", "are used to treat the lungs", "have toxic chemicals", "take care of hair"], "d",
     "التوم «used to treat hair diseases» والحنة «known to be good for the hair». السرطان اتذكر مع الحنة بس."),
    ("We know that the pharaohs had much interest in plants through ……", ["garlic", "paintings", "herbs", "food"], "b",
     "الدليل: «Paintings in the tombs of the pharaohs show that plants were being used… for medical purposes»."),
])

# 19 -----------------------------------------------------------------
passage([
    "While the world was getting into the new year's celebration, David was driving his cab through the crowded streets. After losing his wife to the COVID-19 pandemic four years ago, David spent most of his time working, driving his cab day and night as if nothing had happened. Inside, however, he was suffering.",
    "He was lost in his thoughts when a man hailed him for a ride. He was well dressed and had a bunch of gifts in his hands. The destination was quite far. A few minutes later, the passenger started chatting with David. After a while, David asked Jack if he was new to the city or visiting someone here. \"I have been in Canada for two years. It feels great coming home after such a long time. The best thing is, they have no idea I'm coming,\" replied Jack, animatedly. \"Sounds like you have a big loving family,\" said David. \"A very big family, yes. I have missed them a lot,\" Jack replied. A lucky man, David wondered.",
    "When they reached their destination, Jack got out of the car and invited David for a cup of coffee. Just as David got out of the cab, 8 children rushed outside laughing and screaming. It was an orphanage and Jack considered these children his. David was standing in disbelief. All of the children's faces were glowing with happiness. At that moment, David learned that happiness grows when shared. And after a long time, he was smiling again.",
], [
    ("David works as a/an ……", ["commuter", "traveller", "driver", "porter"], "c",
     "الدليل: «David was driving his cab» = سواق تاكسي."),
    ("Jack had …… children.", ["four", "five", "eight", "no"], "c",
     "الدليل: «8 children rushed outside… Jack considered these children his». هو بيعتبر أطفال الملجأ الـ 8 ولاده."),
    ("David's wife died in ……", ["2017", "2018", "2019", "2020"], "d",
     "ماتت في وباء كوفيد-19. الرقم 19 في الاسم معناه إن الفيروس اتكشف آخر سنة 2019، لكن الوباء (pandemic) نفسه انتشر والناس بدأت تموت بيه من أول 2020 (أول وفاة اتسجلت في يناير 2020). يعني 2017 و2018 و2019 مستحيلين، والإجابة 2020."),
    ("David …… Jack as he had a big loving family.", ["considered", "envied", "wondered", "enlarged"], "b",
     "الدليل: «A lucky man, David wondered». ديفيد اللي فقد مراته حس إن جاك محظوظ = حسده/غبطه = envied."),
    ("According to the passage, \"glowing\" gives the same meaning as ……", ["glooming", "shading", "darkening", "shining"], "d",
     "معنى faces were glowing with happiness إن الوشوش منورة من الفرحة، يعني shining. التلاتة التانيين معناهم ضلمة."),
    ("Jack was a …… man.", ["miserable", "hospitable", "hateful", "nasty"], "b",
     "جاك عزم ديفيد على قهوة وبيرعى أطفال ملجأ = كريم ومضياف = hospitable."),
    ("David finally realized that …… comes from sharing others' cares.", ["sadness", "happiness", "grief", "regret"], "b",
     "الدليل: «David learned that happiness grows when shared»."),
])

# 20 -----------------------------------------------------------------
passage([
    "Man's life has been subject to a lot of changes during the last hundred years, particularly in what is connected with his consuming habits. Sixty years ago, before the start of the consumer societies of today's world, people did not throw away so many of the things they used. They re-used bottles, jars, cardboard boxes and paper bags much more carefully than we do today. Nowadays, we are returning to the same good idea, which we now call \"recycling\".",
    "We can re-think what we throw out. Why do we throw away so much food packaging, so many plastic supermarket bags, old newspapers, old books, bottles and cans? What are all these heaps of waste doing to our environment? Can't we use some of this refuse again? The answer is: yes, we can.",
    "New recycling industries are starting to reuse some of our rubbish. For example, the island of Taiwan now buys waste paper from the USA and recycles it to make newspaper, and for use in offices and homes. Japan takes scrap metal from the USA and makes some new parts with it. Most European and American cities now have \"recycling centres\" for people's old bottles and newspapers. As a matter of fact, recycling is not only good for the environment, but it is good business, too.",
], [
    ("The best title for this passage is ……", ["The Pros and Cons of Recycling", "An Old Habit People Need Nowadays", "Recycling Harms the Environment", "A Bad Habit We Miss"], "b",
     "الناس زمان كانوا بيعيدوا استخدام الحاجات، و«Nowadays, we are returning to the same good idea… recycling» = عادة قديمة محتاجينها دلوقتي. مفيش عيوب للتدوير في القطعة."),
    ("Recycling our rubbish means ……", ["throwing it away", "keeping it", "using it again", "burning it"], "c",
     "الدليل: «Can't we use some of this refuse again?… New recycling industries are starting to reuse some of our rubbish»."),
    ("The pronoun \"it\" in \"recycles it to make newspaper\" refers to ……", ["paper", "Taiwan", "the USA", "metal"], "a",
     "الجملة: «Taiwan now buys waste paper from the USA and recycles it»، يعني it هي الورق القديم (paper)."),
    ("What \"change\" does the writer refer to in the first paragraph?", ["People throw many things away all the time.", "People became more wasteful than before.", "People began to recycle old things again.", "People refuse any consuming habits."], "b",
     "التغيير في «consuming habits»: زمان «people did not throw away so many of the things»، ومع مجتمعات الاستهلاك بقوا يرموا أكتر = أكثر إسرافًا. أما c (رجعوا لإعادة الاستخدام) فده اللي بيحصل دلوقتي كرد فعل، مش التغيير اللي حصل في عادات الاستهلاك."),
    ("Without recycling, people will ……", ["suffer from more environmental problems", "solve all the environmental issues", "buy more newspapers", "increase their good habits"], "a",
     "الكاتب بيسأل «What are all these heaps of waste doing to our environment?» وبيقول التدوير «good for the environment». من غيره مشاكل البيئة تزيد."),
    ("The USA …… scrap metal to Japan.", ["borrows", "exports", "imports", "crushes"], "b",
     "الجملة «Japan takes scrap metal from the USA» يعني أمريكا بتصدّر (exports) واليابان بتستورد."),
    ("Our grandparents were …… than we are today.", ["less careful", "more careless", "more economical", "less wise"], "c",
     "الدليل: «They re-used bottles, jars… much more carefully than we do today» = أكثر توفيرًا = more economical."),
])

# 21 -----------------------------------------------------------------
passage([
    "From far out in space, the Earth looks like a blue ball. Since water covers three-fourths of the Earth's surface, blue is the colour we see most. The continents look brown, like small islands floating in the huge, blue sea. The Earth is shaped like a sphere or a ball. It is 25,000 miles around! It would take more than a year to walk around the whole planet. A spaceship can fly around the widest part of the sphere in only 90 minutes.",
    "Even though spaceships have travelled to the Moon, people cannot visit the Moon without special suits. The Moon has no air or water. Astronauts first landed on the Moon in 1969. After that, there were six more trips to the Moon. They brought back Moon rocks, which scientists are still studying.",
    "The Sun is the closest star to Earth. A star is a hot ball of burning gas. The Sun looks very big because it is so close. But the Sun is just a medium-sized star. Billions of far-away stars are much bigger than our Sun. The burning gases from the Sun are so hot that they warm the Earth from 93 million miles away! Even though the Sun is always shining, the night here on Earth is dark. That's because the Earth rotates, or turns around, every 24 hours. During the day, the Earth faces the Sun. Then we see light. During the night, the Earth turns away from the Sun. Then it faces the darkness of space.",
], [
    ("According to the passage, man went to the Moon …… times.", ["six", "seven", "eight", "nine"], "b",
     "القطعة: «first landed on the Moon in 1969. After that, there were six more trips» = 1 + 6 = 7. (معلومة: تاريخيًا رحلة أبولو 13 ما نزلتش على القمر، فالهبوط الفعلي 6 مرات، لكن الامتحان بيمشي على القطعة.)"),
    ("Our Earth is a ……", ["star", "sun", "planet", "plant"], "c",
     "الدليل: «It would take more than a year to walk around the whole planet». الأرض كوكب، والشمس هي النجم."),
    ("The pronoun \"it\" in \"The Sun looks very big because it is so close\" refers to ……", ["the Moon", "space", "the Sun", "the Earth"], "c",
     "الشمس كبيرة في عينينا لأنها قريبة: it = the Sun."),
    ("The antonym of the word \"closest\" is ……", ["largest", "biggest", "farthest", "nearest"], "c",
     "كلمة closest معناها الأقرب، وعكسها farthest يعني الأبعد. أما nearest فمرادف مش عكس."),
    ("…… are still studying Moon rocks.", ["Scientists", "Doctors", "Astrologers", "Botanists"], "a",
     "الدليل: «Moon rocks, which scientists are still studying». astrologers = المنجمين (مش علماء)."),
    ("From space, the Earth looks like ……", ["a star", "a blue ball", "space", "the Moon"], "b",
     "أول جملة: «From far out in space, the Earth looks like a blue ball»."),
    ("The Sun is so close to the Earth that it looks ……", ["huge", "small", "light", "distant"], "a",
     "الدليل: «The Sun looks very big because it is so close» = huge."),
])

# 22 -----------------------------------------------------------------
passage([
    "Many researchers, engineers and environmentalists are expressing deep concern about changes in the overall climate of the planet. Fossil fuels are continuously used to produce electricity. The burning of these fuels produces gases like carbon dioxide, methane and nitrous oxides, which lead to global warming. Desertification also leads to warmer temperatures. The hazard of global warming is continuously causing major damage to the earth's environment.",
    "Most people are still unaware of global warming and don't consider it a big problem in the years to come. What most people don't understand is that global warming is currently happening and we are already experiencing some of its withering effects. It severely affects ecosystems and disturbs the ecological balance; therefore, some solutions must be devised.",
    "Alternative energy sources – solar, wind, hydro, geothermal and biomass – need to be seriously pursued. Finding and using renewable sources is one of the methods to combat the ever-increasing global warming effectively, since the continuous rise in the temperature of the planet is really upsetting. Much of the heat is absorbed by the oceans, air and land, and this heats up the surface of the planet. Global warming is caused by anthropogenic activities.",
], [
    ("Desertification means …… a wide area of trees.", ["clearing", "planting", "irrigating", "spraying"], "a",
     "التصحر (desertification) يعني أرض كانت خضرا تتحول لصحرا، ومن أكبر أسبابه إزالة الشجر والنباتات من مساحة كبيرة، فأقرب اختيار clearing. والقطعة بتقول إنه «leads to warmer temperatures». أما planting وirrigating (الري) فعكس التصحر."),
    ("The word \"its\" in \"some of its withering effects\" refers to ……", ["desertification", "global warming", "carbon dioxide", "the environment"], "b",
     "الجملة: «global warming is currently happening and we are already experiencing some of its withering effects»، يعني آثار الاحتباس الحراري."),
    ("Scientists recommend …… fossil fuels in an attempt to solve the problem.", ["using", "misusing", "reducing", "reusing"], "c",
     "حرق الوقود الحفري سبب المشكلة، والحل «Alternative energy sources… renewable sources» يعني نقلل الوقود الحفري = reducing."),
    ("Burning fossil fuels …… global warming.", ["causes of", "results of", "leads to", "results from"], "c",
     "الدليل: «The burning of these fuels produces gases… which lead to global warming». (causes بعدها مفعول على طول من غير of.)"),
    ("The synonym of the word \"ecological\" is ……", ["environmental", "biological", "chemical", "material"], "a",
     "معنى ecological balance التوازن البيئي، فكلمة ecological معناها environmental (له علاقة بالبيئة)."),
    ("According to the passage, we …… the destructive effects of global warming.", ["will face", "faced", "have never faced", "are already facing"], "d",
     "الدليل: «we are already experiencing some of its withering effects»."),
    ("The best title for this passage is \"……\".", ["National Disasters", "Global Disasters", "Trees and Nature", "Anthropogenic Activities"], "b",
     "القطعة عن الاحتباس الحراري (Global warming) اللي بيضر كوكب الأرض كله = كارثة عالمية. «National» محلية بس."),
])

# 23 -----------------------------------------------------------------
passage([
    "\"Necessity is the mother of invention\" is a famous common proverb which means that our needs always motivate our minds to create new things in order to manage well in a world full of speedy changes. Man's needs have often directed him to discover the natural resources around him, and to make with his own hands the things he wants. Thus, he made tools to cultivate the land and get its crops. Those tools played an important part in establishing civilization.",
    "Food, clothing and shelter are still considered to be man's basic needs. The progress of technology has enabled man to satisfy all these needs. It has helped him to take wide steps in developing agriculture, industry and public services. Thus, we are now enjoying the blessings of modern civilization.",
    "When civilization developed and man lived in organized societies, he found himself in need of more than his necessities. Education is next to food in importance because it is the only way to acquire experience and the qualifications necessary to earn a living. Education changed our style of living and led to higher thinking levels. Man invaded space. He invented the computer. No wonder that man has great abilities which will enable him to create more inventions in the future.",
], [
    ("The word \"acquire\" has a similar meaning to ……", ["require", "demand", "obtain", "contain"], "c",
     "معنى acquire experience يكتسب خبرة، يعني obtain (يحصل على). أما require وdemand فمعناهم يطلب."),
    ("According to the passage, education is of great importance because ……", ["it gives us experience and a way of earning a living", "it is prior to food in importance", "it is a natural resource before us", "the tools played a role in our civilization"], "a",
     "الدليل: «it is the only way to acquire experience and the qualifications necessary to earn a living». والتعليم «next to food» يعني بعد الأكل مش قبله."),
    ("Man needed more than his necessities when he ……", ["needed tools", "lived in organized societies", "discovered natural resources", "made the things he wanted"], "b",
     "الدليل: «When civilization developed and man lived in organized societies, he found himself in need of more than his necessities»."),
    ("\"He made tools to cultivate the land.\" Another word for \"cultivate\" is ……", ["ignore", "destroy", "plant", "abandon"], "c",
     "معنى cultivate the land يزرع الأرض، يعني plant. التلاتة التانيين عكس المعنى."),
    ("According to the passage, the need for collecting the crops led man to ……", ["plant huge areas of land", "invent agricultural tools", "buy machines", "hire peasants to help him"], "b",
     "الدليل: «he made tools to cultivate the land and get its crops»."),
    ("In the last paragraph, invading space and inventing the computer are evidence that ……", ["man spends a lot of money", "man has extraordinary abilities", "science is obtainable", "space exploration is not impossible"], "b",
     "الدليل بعدها على طول: «No wonder that man has great abilities»."),
    ("The main idea of the passage is \"……\".", ["Necessities can be postponed", "Conditions create inventions", "The needs are motivated by possibilities", "The agriculture and civilization"], "b",
     "الفكرة كلها في المثل: «Necessity is the mother of invention»، يعني احتياجاتنا وظروفنا بتدفعنا نخترع، وده معنى Conditions create inventions. أما الزراعة والحضارة فمثال في القطعة مش الفكرة الأساسية."),
])

# 24 -----------------------------------------------------------------
passage([
    "Walking in the street at night, I found a purse full of money and an identity card. I found a photo of a pretty young lady. I put it back in the purse and went directly to the police station. The sergeant made a note of my name and address.",
    "Last Friday, I was invited to a party at my friend's house in Shoubra. A neighbour of my friend came to visit his wife. When I looked at her face, I found it familiar to me although we hadn't met before. After a short time, I remembered that she was the lady I had seen in the photo. I was able to describe the purse and the sum of money accurately. She was surprised and we went together to the police station to get the purse back. After getting out of the police station, she thanked me a lot. She told me that she had looked for her purse for a long time until she lost hope of finding it. I went home feeling happy as I was able to make this lady happy. It is good to feel satisfied with yourself.",
], [
    ("The writer met the purse owner at ……", ["the police station", "the street", "their first school", "his friend's house"], "d",
     "الدليل: «I was invited to a party at my friend's house in Shoubra. A neighbour of my friend came to visit his wife»."),
    ("The word …… in the passage is the antonym of the word \"exotic\".", ["abnormal", "familiar", "purse", "accurate"], "b",
     "كلمة exotic معناها غريب أو أجنبي، وعكسها familiar يعني مألوف. والكلمة موجودة في القطعة: «I found it familiar to me»."),
    ("This passage is extracted from a ……", ["comic", "science book", "religion book", "story"], "d",
     "حكاية بضمير المتكلم فيها أحداث وشخصيات = story."),
    ("The moral lesson is ……", ["feeling happy", "walking in the street", "finding a purse", "making others happy"], "d",
     "الدليل: «I went home feeling happy as I was able to make this lady happy». المغزى: إسعاد الآخرين (والأمانة) بيرضيك عن نفسك."),
    ("If the lady hadn't visited her friend's wife, she would ……", ["not know about her purse", "not forget about her purse", "forget about the money", "find her purse"], "a",
     "هي كانت فقدت الأمل «until she lost hope of finding it»، وعرفت مكانها بس لما قابلت الكاتب في الزيارة. من غيرها ما كانتش هتعرف حاجة عن شنطتها."),
    ("If you find a sum of money, it's honest to ……", ["give it to the police", "give it to your friends", "share it with others", "share it with the police"], "a",
     "زي الكاتب: «went directly to the police station». ده التصرف الأمين."),
    ("The word \"satisfied\" means ……", ["angry", "happy", "cross", "nervous"], "b",
     "كلمة satisfied معناها راضي ومبسوط، يعني happy. أما angry وcross فمعناهم زعلان."),
])

# 25 -----------------------------------------------------------------
passage([
    "Sports are full of wonderful moments, but perhaps nothing is as exciting as the finish of the marathon. It is the longest and hardest race of all. The name marathon came from a village in Greece. A famous battle was fought there in the year 490 BC. When the Greeks had beaten the Persians, a soldier ran the way from Marathon to Athens, more than 40 kilometres, to tell people the good news. When the modern Olympic Games started in 1890, the organizers knew the story. The marathon has been a race ever since.",
    "In the ancient world, the Olympics were held every four years. They were an important part of life. In modern games we try to copy their ideas. The finest sportsmen in the world gather in one place – or at least, the finest amateurs do. An amateur is someone who does not earn any money from sports. It is often difficult to say who is an amateur and who is not.",
    "It is true that some Olympic athletes do earn a large amount of money, like professional sportsmen. But most Olympic athletes are students, teachers or people with other jobs. They have to spend a lot of money on training. Their governments pay for their training, travel and pocket money because they want them to win.",
], [
    ("The marathon is the …… race of all.", ["longest", "most modern", "fastest", "slowest"], "a",
     "الدليل: «It is the longest and hardest race of all»."),
    ("An amateur is someone who …… from sport.", ["doesn't earn any money", "earns much money", "earns little money", "earns no money"], "a",
     "الدليل بالنص: «An amateur is someone who does not earn any money from sports». (الاختيار d نفس المعنى، بس a هو كلام القطعة بالحرف، وده المطلوب.)"),
    ("The name marathon came from ……", ["a story", "a village in Greece", "a race", "a toy"], "b",
     "الدليل: «The name marathon came from a village in Greece»."),
    ("The …… Olympic Games were started in 1890.", ["ancient", "modern", "old", "traditional"], "b",
     "الدليل: «When the modern Olympic Games started in 1890»."),
    ("A lot of money is needed for Olympic athletes because ……", ["the governments need teachers", "Olympic athletes have to spend a lot of money on training", "the Olympics were held every four years", "the Olympic Games were started in 1890"], "b",
     "الدليل: «They have to spend a lot of money on training»."),
    ("The modern Olympic Games were started in ……", ["1800", "1980", "490", "1890"], "d",
     "على حسب القطعة: «started in 1890». (معلومة: تاريخيًا أول دورة أولمبية حديثة كانت في أثينا سنة 1896، بس الإجابة من القطعة 1890.)"),
    ("The word \"amateur\" in the passage means ……", ["not professional", "modern", "ancient", "very old"], "a",
     "كلمة amateur معناها هاوي مش محترف، بيلعب من غير فلوس، يعني not professional."),
])
