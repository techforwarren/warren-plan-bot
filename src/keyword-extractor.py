# TODO: 
#       def function to feed plan list from db or .json file to populate plans return synonym list if auto processing
#       is desired.  
#       Otherwise, write output to file or firestore.
#       Add imports to requirements if function created for future use. 

import RAKE
import nltk
import json
from nltk.corpus import stopwords



plans = {
    "plans": [{
        "id": 1,
        "topic": "student debt",
        "summary": "She believes we should treat higher education like our public school system - free and accessible to all Americans. That's why she's calling for something truly transformational - the cancellation of up to $50,000 in student loan debt for 42 million Americans and free universal college for everyone.",
        "display_title": "Cancellation of Student Loan Debt and Universal Free Public College",
        "url": "https://medium.com/@teamwarren/im-calling-for-something-truly-transformational-universal-free-public-college-and-cancellation-of-a246cd0f910f",
        "keyword_synonyms": []
    }, {
        "id": 2,
        "topic": "immigration reform",
        "summary": "Immigrants are our neighbors and our friends. But an immigration system that can't tell the difference between a terrorist and a little girl is badly broken. That's why She believes immigration reform must include a rules-based system that protects our security, grows our economy, and reflects our values.",
        "display_title": "A Fair and Welcoming Immigration System",
        "url": "https://medium.com/@teamwarren/a-fair-and-welcoming-immigration-system-8fff69cd674e",
        "keyword_synonyms": []
    }, {
        "id": 3,
        "topic": "wall street reform",
        "summary": "For decades, Washington has lived by a simple rule: If it's good for Wall Street, it's good for the economy. But for a long time now, Wall Street's success hasn't helped the broader economy - it's come at the expense of the rest of the economy. She's plan shuts down the Wall Street giveaways and reins in the financial industry so that it stops sucking money out of the rest of the economy.",
        "display_title": "End Wall Street's Stranglehold on Our Economy",
        "url": "https://medium.com/@teamwarren/end-wall-streets-stranglehold-on-our-economy-70cf038bac76",
        "keyword_synonyms": []
    }, {
        "id": 4,
        "topic": "strong economy",
        "summary": "She rang the alarm before the 2008 financial crisis -- but Congress and regulators didn't listen. Now she's seeing warning signs in our economy again. She believes we need to take concrete steps now to shore up our economy and reduce the risk of economic shocks if we want to reduce the chances of another crash.",
        "display_title": "The Next Economic Crash -- And How to Stop It",
        "url": "https://medium.com/@teamwarren/the-coming-economic-crash-and-how-to-stop-it-355703da148b",
        "keyword_synonyms": []
    }, {
        "id": 5,
        "topic": "clean green energy",
        "summary": "Climate change is real, it's man-made, and our government needs to take bold action and use all the tools available to combat it before it's too late. Building on some of her earlier plans to address climate change, She's new plan attacks it by using the power of public markets to accelerate the adoption of clean energy.",
        "display_title": "Accelerate the Transition to Clean Energy",
        "url": "https://medium.com/@teamwarren/accelerating-the-transition-to-clean-energy-46af492d8c57",
        "keyword_synonyms": []
    }, {
        "id": 6,
        "topic": "pay for women of color",
        "summary": "Our economy should be working just as hard for women of color as women of color work for our economy and their families, but for decades, the government has helped perpetuate the systemic discrimination that has denied women of color fair pay and equal opportunities. That's why She has a new plan: a set of executive actions she will take on day one of the Warren Administration to boost wages for women of color and open up new pathways to the leadership positions they deserve.",
        "display_title": "Valuing the Work of Women of Color",
        "url": "https://medium.com/@teamwarren/valuing-the-work-of-women-of-color-c652bf6ccc9a",
        "keyword_synonyms": []
    }, {
        "id": 7,
        "topic": "diplomacy",
        "summary": "American security and prosperity depend on robust diplomacy, but Donald Trump has declared war on our State Department through a toxic combination of malice and neglect. She has a plan to rebuild the State Department by doubling the size of the foreign service and recruiting and retaining a bold, diverse, and professional 21st century diplomatic corps. She is also making a commitment to end the corrupt practice of selling cushy diplomatic posts to wealthy donors. She won't give ambassadorial posts to wealthy donors or bundlers -- and she's calling on everyone running for President to do the same.",
        "display_title": "Revitalizing Diplomacy: A 21st Century Foreign Service",
        "url": "https://medium.com/@teamwarren/revitalizing-diplomacy-a-21st-century-foreign-service-2d9d195698f",
        "keyword_synonyms": []
    }, {
        "id": 8,
        "topic": "election reform",
        "summary": "It's time to make voting easy and convenient, stop racist voter suppression, and secure our elections. She's plan creates uniform federal rules to make voting easy for everyone - no registration problems, no purges, no difficulties voting, and no gerrymandering - and we'll have federal funding to make sure our elections are secure from hacking.",
        "display_title": "Her Plan to Strengthen Our Democracy",
        "url": "https://medium.com/@teamwarren/my-plan-to-strengthen-our-democracy-6867ec1bcd3c",
        "keyword_synonyms": []
    }, {
        "id": 9,
        "topic": "for profit prison reform",
        "summary": "Washington hands billions over to private prison and detention companies that profit off of inhumane detention and incarceration policies. That stops now. Her plan will root out the profit interests standing in the way of real reform by banning privately-owned facilities and preventing companies from exploiting those caught in our criminal and immigration systems.",
        "display_title": "Ending Private Prisons  and Exploitation for Profit",
        "url": "https://medium.com/@teamwarren/ending-private-prisons-and-exploitation-for-profit-cb6dea67e913",
        "keyword_synonyms": []
    }, {
        "id": 10,
        "topic": "minority business owners",
        "summary": "Generations of government discrimination have denied Black and other minority families opportunities to build wealth, making it harder for them to start a successful business and holding back our economy. Her new plan provides $7 billion in funding to help level the playing field, and support 100,000 small businesses and more than a million jobs.",
        "display_title": "Leveling the Playing Field for Entrepreneurs",
        "url": "https://medium.com/@teamwarren/leveling-the-playing-field-for-entrepreneurs-2a585aa2b6d7",
        "keyword_synonyms": []
    }, {
        "id": 11,
        "topic": "American jobs",
        "summary": "For decades, we've let giant corporations run our economy even though they have no loyalty or allegiance to America. Not on her watch. She will use all the tools of government to defend and create good American jobs.",
        "display_title": "The New American Patriotism",
        "url": "https://medium.com/@teamwarren/a-plan-for-economic-patriotism-13b879f4cfc7",
        "keyword_synonyms": []
    }, {
        "id": 12,
        "topic": "green energy jobs",
        "summary": "By investing $2 trillion in American research and American manufacturing of clean energy technology, we can lead the global effort to combat climate change, boost our economy, and create more than a million good jobs here at home.",
        "display_title": "A Green Manufacturing Plan",
        "url": "https://medium.com/@teamwarren/my-green-manufacturing-plan-for-america-fc0ad53ab614",
        "keyword_synonyms": []
    }, {
        "id": 13,
        "topic": "crimes by the president",
        "summary": "Impeachment isn't supposed to be the only way that a President can be held accountable for committing a crime. Congress should make it clear that Presidents can be indicted for criminal activity, including obstruction of justice. And when She'sPresident, I'll appoint Justice Department officials who will reverse flawed policies so no President is shielded from criminal accountability.",
        "display_title": "Plan to Make Sure That No President is Above the Law",
        "url": "https://medium.com/@teamwarren/no-president-is-above-the-law-f4812e580336",
        "keyword_synonyms": []
    }, {
        "id": 14,
        "topic": "reproductive rights",
        "summary": "Our democracy should not be held hostage by right-wing courts, and women should not have to hope that Brett Kavanaugh and Donald Trump's Supreme Court will respect the law. Congress should pass new federal laws that protect access to reproductive care from right-wing ideologues in the states. Federal laws that ensure real access to birth control and abortion care for all women. Federal laws that will stand no matter what the Supreme Court does.",
        "display_title": "Congressional Action to Protect Choice",
        "url": "https://medium.com/@teamwarren/congressional-action-to-protect-choice-aaf94ed25fb5",
        "keyword_synonyms": []
    }, {
        "id": 15,
        "topic": "military lobbyists",
        "summary": "The revolving door between defense lobbyists, Congress, and the Pentagon tilts countless decisions away from legitimate national security interests and toward the desires of giant defense contractors. It's past time to cut our bloated defense budget - and to get serious about cutting defense spending, we need to reduce corporate influence. Americans deserve to know that our military is making decisions with only one thing in mind: their safety. That's why She's introducing her plan to slam shut the revolving door and curb the influence of giant defense contractors on the Pentagon.",
        "display_title": " Reduce Corporate Influence at the Pentagon",
        "url": "https://medium.com/@teamwarren/its-time-to-reduce-corporate-influence-at-the-pentagon-98f52ee0fcf1",
        "keyword_synonyms": []
    }, {
        "id": 16,
        "topic": "national security climate change",
        "summary": "Climate change is real, it is worsening by the day, and it is undermining our military readiness. But instead of meeting this threat head-on, Washington is ignoring it - and making it worse. She has a plan to make the U.S. military more resilient to climate change, and to leverage its huge energy footprint as part of our climate solution. Her energy and climate resiliency plan will improve our service members' readiness and safety, all while achieving cost savings for American taxpayers.",
        "display_title": "National Security & Climate Change",
        "url": "https://medium.com/@teamwarren/our-military-can-help-lead-the-fight-in-combating-climate-change-2955003555a3",
        "keyword_synonyms": []
    }, {
        "id": 17,
        "topic": "opioid crisis",
        "summary": "Every day, 130 Americans die from an opioid overdose. This is a public health crisis - and we need to start treating it like one. That's why Congressman Elijah Cummings and She are rolling out the CARE Act, a comprehensive plan that invests $100 billion over the next ten years in states and communities that are on the frontlines of the epidemic - to provide prevention, treatment, and recovery services for those who need it most.",
        "display_title": "Tackling the Opioid Crisis Head On",
        "url": "https://medium.com/@teamwarren/my-comprehensive-plan-to-end-the-opioid-crisis-9d85deaa3ccb",
        "keyword_synonyms": []
    }, {
        "id": 18,
        "topic": "Puerto Rico debt relief",
        "summary": "After Hurricanes Irma and Maria devastated Puerto Rico, one of the biggest constraints holding back the island's recovery has been its debt. If Puerto Rico were a big company or an American city, it could file for bankruptcy, but because of its unique status, those legal options aren't available. That's why She has a plan to provide comprehensive debt relief to Puerto Rico so it can rebuild and thrive.",
        "display_title": "Providing Debt Relief for Puerto Rico",
        "url": "https://medium.com/@teamwarren/my-plan-to-provide-comprehensive-debt-relief-to-puerto-rico-f8b575a81b06",
        "keyword_synonyms": []
    }, {
        "id": 19,
        "topic": "maternal mortality",
        "summary": "We are facing a maternal mortality crisis in America. And for Black moms, it's an epidemic. One major reason? Racism. It's time to hold health systems accountable for preventable failures and demand change - because women's lives depend on it.",
        "display_title": "Addressing Our Maternal Mortality Epidemic",
        "url": "https://www.essence.com/feature/sen-elizabeth-warren-black-women-mortality-essence/",
        "keyword_synonyms": []
    }, {
        "id": 20,
        "topic": "military housing",
        "summary": "Our military families have been raising the alarm about their living conditions for years. This stops now. She has a plan to improve our military housing, protect families from abuse, and hold private developers accountable for the promises they make to those who serve our country.",
        "display_title": "Improving Our Military Housing",
        "url": "https://medium.com/@teamwarren/my-plan-to-improve-our-military-housing-b1a46ba235b8",
        "keyword_synonyms": []
    }, {
        "id": 21,
        "topic": "student debt cancellation universal free public college",
        "summary": "We should treat higher education like our public school system - free and accessible to all Americans. That's why She'scalling for something truly transformational - the cancellation of up to $50,000 in student loan debt for 42 million Americans and free universal college for everyone.",
        "display_title": "Cancellation of Student Loan Debt and Universal Free Public College",
        "url": "https://medium.com/@teamwarren/im-calling-for-something-truly-transformational-universal-free-public-college-and-cancellation-of-a246cd0f910f",
        "keyword_synonyms": []
    }, {
        "id": 22,
        "topic": "public land management",
        "summary": "She'smaking a promise. On the first day of a Warren administration, She will sign a moratorium so that there is no more drilling on public lands, and She will set a goal of providing 10 percent of our overall electricity generation from renewable sources. Climate change is here, it is real, and we should make our public lands part of the solution.",
        "display_title": "Public Lands",
        "url": "https://medium.com/@teamwarren/my-plan-for-public-lands-e4be1d88a01c",
        "keyword_synonyms": []
    }, {
        "id": 22,
        "topic": "corporate taxes",
        "summary": "Year after year, some of the biggest corporations in the country make huge profits, but pay zero federal corporate income taxes on those profits. That isn't right. Her Real Corporate Profits Tax will raise over a trillion dollars and make sure the biggest corporations pay their fair share.",
        "display_title": "Real Corporate Profits Tax",
        "url": "https://medium.com/@teamwarren/im-proposing-a-big-new-idea-the-real-corporate-profits-tax-29dde7c960d",
        "keyword_synonyms": []
    }, {
        "id": 23,
        "topic": "ceo accountability",
        "summary": "Our justice system should ensure that if you cheat working Americans, you'll go to jail. It's time to reform our laws to make sure that corporate executives are held accountable for overseeing massive scams.",
        "display_title": "Corporate Executive Accountability Act",
        "url": "https://www.washingtonpost.com/opinions/elizabeth-warren-its-time-to-scare-corporate-america-straight/2019/04/02/ca464ab0-5559-11e9-8ef3-fbd41a2ce4d5_story.html",
        "keyword_synonyms": []
    }, {
        "id": 24,
        "topic": "family farms",
        "summary": "Today, a farmer can work hard, do everything right, and still not make it. Her plan gives family farmers a fair shot by tackling consolidation, un-rigging the rules that favor big agribusiness, and standing up for America's farmers against foreign interests.",
        "display_title": "Leveling the Playing Field for America's Family Farmers",
        "url": "https://medium.com/@teamwarren/leveling-the-playing-field-for-americas-family-farmers-823d1994f067",
        "keyword_synonyms": []
    }, {
        "id": 25,
        "topic": "electoral college reform",
        "summary": "Presidential candidates should have to ask every American in every part of the country for their vote. We can make that happen by abolishing the Electoral College and replacing it with a national popular vote.",
        "display_title": "Getting Rid of the Electoral College",
        "url": "https://medium.com/@teamwarren/its-time-to-get-rid-of-the-electoral-college-20efcac09c5e",
        "keyword_synonyms": []
    }, {
        "id": 26,
        "topic": "safe affordable housing",
        "summary": "Every American deserves a safe and affordable place to live. Her plan makes a historic investment in housing that would bring down rents by 10%, create 1.5 million new jobs, and begin closing the racial wealth gap.",
        "display_title": "For Affordable Housing for America",
        "url": "https://medium.com/@teamwarren/my-housing-plan-for-america-20038e19dc26",
        "keyword_synonyms": []
    }, {
        "id": 27,
        "topic": "big tech companies",
        "summary": "America's biggest tech companies are controlling more and more of our digital lives and using their size and power to make it harder for the next tech entrepreneur with the next big idea to compete. It's time to break up the biggest tech companies to restore competition - and make sure these corporations don't get so powerful that they undermine our democracy.",
        "display_title": "How We Can Break Up Big Tech",
        "url": "https://medium.com/@teamwarren/heres-how-we-can-break-up-big-tech-9ad9e0da324c",
        "keyword_synonyms": []
    }, {
        "id": 28,
        "topic": "universal child care",
        "summary": "We're the wealthiest country on the planet - high-quality child care and early education shouldn't be a privilege that's only for the rich. She'sfighting to make high-quality child care from birth to school age free for millions of families and affordable for all.",
        "display_title": "Universal Child Care",
        "url": "https://medium.com/@teamwarren/my-plan-for-universal-child-care-762535e6c20a",
        "keyword_synonyms": []
    }, {
        "id": 29,
        "topic": "ultra millionaire tax",
        "summary": "She'sproposing something brand new - a tax on the wealth of the richest Americans. Her Ultra-Millionaire Tax asks the richest 0.1% of Americans to pay their fair share, raising nearly $3 trillion that we can use to rebuild the middle class.",
        "display_title": "The Ultra-Millionaire Tax",
        "url": "https://elizabethwarren.com/ultra-millionaire-tax/",
        "keyword_synonyms": []
    }, {
        "id": 30,
        "topic": "farming economy",
        "summary": "She's plan will help create a new farm economy where family farmers have financial security and the freedom to do what they do best. Farmers of all backgrounds will finally have the economic freedom to pursue diverse, sustainable farming - and get paid up front for doing so. Americans will have a steady and affordable supply of food. Kids in rural communities will have healthy lunches grown in their backyards and packaged at local food hubs run by small town entrepreneurs. Taxpayers won't pay twice - once at the grocery store and once through their taxes - for overproduced commodities. We will replenish our soil and our water to chart a path towards a climate solution and achieve the goals of the Green New Deal.",
        "display_title": "A New Farm Economy",
        "url": "https://medium.com/@teamwarren/a-new-farm-economy-8db50fac0551",
        "keyword_synonyms": []
    }, {
        "id": 31,
        "topic": "gun violence mass shootings",
        "summary": "The majority of Americans, including a majority of gun owners, support common sense gun safety reforms. But for years, those reforms have been blocked by far-right ideologues in Congress bought and paid for by the gun industry and their NRA partners. Enough is enough. My plan to reduce gun violence includes ambitious executive actions and comprehensive legislation to break the influence of the gun lobby and implement real reform that will save lives.",
        "display_title": "Protecting Our Communities from Gun Violence",
        "url": "https://medium.com/@teamwarren/protecting-our-communities-from-gun-violence-a2ebf7abd9be",
        "keyword_synonyms": []
    }]
}

# Extra lists of stopwords that can be substituted for RAKE.StopWordList()
stop_words = ["a", "about", "above", "after", "again", "against", "ain", "all", "am", "an", "and", "any", "are", "aren", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "couldn", "couldn't", "d", "did", "didn", "didn't", "do", "does", "doesn", "doesn't", "doing", "don", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn", "hadn't", "has", "hasn", "hasn't", "have", "haven", "haven't", "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", "isn", "isn't", "it", "it's", "its", "itself", "just", "ll", "m", "ma", "me", "mightn", "mightn't", "more", "most", "mustn", "mustn't", "my", "myself", "needn", "needn't", "no", "nor", "not", "now", "o", "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "re", "s", "same", "shan", "shan't", "she", "she's", "should", "should've", "shouldn", "shouldn't", "so", "some", "such", "t", "than", "that", "that'll", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", "ve", "very", "was", "wasn", "wasn't", "we", "were", "weren", "weren't", "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with", "won", "won't", "wouldn", "wouldn't", "y", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves", "could", "he'd", "he'll", "he's", "here's", "how's", "i'd", "i'll", "i'm", "i've", "let's", "ought", "she'd", "she'll", "that's", "there's", "they'd", "they'll", "they're", "they've", "we'd", "we'll", "we're", "we've", "what's", "when's", "where's", "who's", "why's", "would", "able", "abst", "accordance", "according", "accordingly", "across", "act", "actually", "added", "adj", "affected", "affecting", "affects", "afterwards", "ah", "almost", "alone", "along", "already", "also", "although", "always", "among", "amongst", "announce", "another", "anybody", "anyhow", "anymore", "anyone", "anything", "anyway", "anyways", "anywhere", "apparently", "approximately", "arent", "arise", "around", "aside", "ask", "asking", "auth", "available", "away", "awfully", "b", "back", "became", "become", "becomes", "becoming", "beforehand", "begin", "beginning", "beginnings", "begins", "behind", "believe", "beside", "besides", "beyond", "biol", "brief", "briefly", "c", "ca", "came", "cannot", "can't", "cause", "causes", "certain", "certainly", "co", "com", "come", "comes", "contain", "containing", "contains", "couldnt", "date", "different", "done", "downwards", "due", "e", "ed", "edu", "effect", "eg", "eight", "eighty", "either", "else", "elsewhere", "end", "ending", "enough", "especially", "et", "etc", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "except", "f", "far", "ff", "fifth", "first", "five", "fix", "followed", "following", "follows", "former", "formerly", "forth", "found", "four", "furthermore", "g", "gave", "get", "gets", "getting", "give", "given", "gives", "giving", "go", "goes", "gone", "got", "gotten", "h", "happens", "hardly", "hed", "hence", "hereafter", "hereby", "herein", "heres", "hereupon", "hes", "hi", "hid", "hither", "home", "howbeit", "however", "hundred", "id", "ie", "im", "immediate", "immediately", "importance", "important", "inc", "indeed", "index", "information", "instead", "invention", "inward", "itd", "it'll", "j", "k", "keep", "keeps", "kept", "kg", "km", "know", "known", "knows", "l", "largely", "last", "lately", "later", "latter", "latterly", "least", "less", "lest", "let", "lets", "like", "liked", "likely", "line", "little", "'ll", "look", "looking", "looks", "ltd", "made", "mainly", "make", "makes", "many", "may", "maybe", "mean", "means", "meantime", "meanwhile", "merely", "mg", "might", "million", "miss", "ml", "moreover", "mostly", "mr", "mrs", "much", "mug", "must", "n", "na", "name", "namely", "nay", "nd", "near", "nearly", "necessarily", "necessary", "need", "needs", "neither", "never", "nevertheless", "new", "next", "nine", "ninety", "nobody", "non", "none", "nonetheless", "noone", "normally", "nos", "noted", "nothing", "nowhere", "obtain", "obtained", "obviously", "often", "oh", "ok", "okay", "old", "omitted", "one", "ones", "onto", "ord", "others", "otherwise", "outside", "overall", "owing", "p", "page", "pages", "part", "particular", "particularly", "past", "per", "perhaps", "placed", "please", "plus", "poorly", "possible", "possibly", "potentially", "pp", "predominantly", "present", "previously", "primarily", "probably", "promptly", "proud", "provides", "put", "q", "que", "quickly", "quite", "qv", "r", "ran", "rather", "rd", "readily", "really", "recent", "recently", "ref", "refs", "regarding", "regardless", "regards", "related", "relatively", "research", "respectively", "resulted", "resulting", "results", "right", "run", "said", "saw", "say", "saying", "says", "sec", "section", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sent", "seven", "several", "shall", "shed", "shes", "show", "showed", "shown", "showns", "shows", "significant", "significantly", "similar", "similarly", "since", "six", "slightly", "somebody", "somehow", "someone", "somethan", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "specifically", "specified", "specify", "specifying", "still", "stop", "strongly", "sub", "substantially", "successfully", "sufficiently", "suggest", "sup", "sure", "take", "taken", "taking", "tell", "tends", "th", "thank", "thanks", "thanx", "thats", "that've", "thence", "thereafter", "thereby", "thered", "therefore", "therein", "there'll", "thereof", "therere", "theres", "thereto", "thereupon", "there've", "theyd", "theyre", "think", "thou", "though", "thoughh", "thousand", "throug", "throughout", "thru", "thus", "til", "tip", "together", "took", "toward", "towards", "tried", "tries", "truly", "try", "trying", "ts", "twice", "two", "u", "un", "unfortunately", "unless", "unlike", "unlikely", "unto", "upon", "ups", "us", "use", "used", "useful", "usefully", "usefulness", "uses", "using", "usually", "v", "value", "various", "'ve", "via", "viz", "vol", "vols", "vs", "w", "want", "wants", "wasnt", "way", "wed", "welcome", "went", "werent", "whatever", "what'll", "whats", "whence", "whenever", "whereafter", "whereas", "whereby", "wherein", "wheres", "whereupon", "wherever", "whether", "whim", "whither", "whod", "whoever", "whole", "who'll", "whomever", "whos", "whose", "widely", "willing", "wish", "within", "without", "wont", "words", "world", "wouldnt", "www", "x", "yes", "yet", "youd", "youre", "z", "zero", "a's", "ain't", "allow", "allows", "apart", "appear", "appreciate", "appropriate", "associated", "best", "better", "c'mon", "c's", "cant", "changes", "clearly", "concerning", "consequently", "consider", "considering", "corresponding", "course", "currently", "definitely", "described", "despite", "entirely", "exactly", "example", "going", "greetings", "hello", "help", "hopefully", "ignored", "inasmuch", "indicate", "indicated", "indicates", "inner", "insofar", "it'd", "keep", "keeps", "novel", "presumably", "reasonably", "second", "secondly", "sensible", "serious", "seriously", "sure", "t's", "third", "thorough", "thoroughly", "three", "well", "wonder", "a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and", "another", "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are", "around", "as", "at", "back", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven", "else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "co", "op", "research-articl", "pagecount", "cit", "ibid", "les", "le", "au", "que", "est", "pas", "vol", "el", "los", "pp", "u201d", "well-b", "http", "volumtype", "par", "0o", "0s", "3a", "3b", "3d", "6b", "6o", "a1", "a2", "a3", "a4", "ab", "ac", "ad", "ae", "af", "ag", "aj", "al", "an", "ao", "ap", "ar", "av", "aw", "ax", "ay", "az", "b1", "b2", "b3", "ba", "bc", "bd", "be", "bi", "bj", "bk", "bl", "bn", "bp", "br", "bs", "bt", "bu", "bx", "c1", "c2", "c3", "cc", "cd", "ce", "cf", "cg", "ch", "ci", "cj", "cl", "cm", "cn", "cp", "cq", "cr", "cs", "ct", "cu", "cv", "cx", "cy", "cz", "d2", "da", "dc", "dd", "de", "df", "di", "dj", "dk", "dl", "do", "dp", "dr", "ds", "dt", "du", "dx", "dy", "e2", "e3", "ea", "ec", "ed", "ee", "ef", "ei", "ej", "el", "em", "en", "eo", "ep", "eq", "er", "es", "et", "eu", "ev", "ex", "ey", "f2", "fa", "fc", "ff", "fi", "fj", "fl", "fn", "fo", "fr", "fs", "ft", "fu", "fy", "ga", "ge", "gi", "gj", "gl", "go", "gr", "gs", "gy", "h2", "h3", "hh", "hi", "hj", "ho", "hr", "hs", "hu", "hy", "i", "i2", "i3", "i4", "i6", "i7", "i8", "ia", "ib", "ic", "ie", "ig", "ih", "ii", "ij", "il", "in", "io", "ip", "iq", "ir", "iv", "ix", "iy", "iz", "jj", "jr", "js", "jt", "ju", "ke", "kg", "kj", "km", "ko", "l2", "la", "lb", "lc", "lf", "lj", "ln", "lo", "lr", "ls", "lt", "m2", "ml", "mn", "mo", "ms", "mt", "mu", "n2", "nc", "nd", "ne", "ng", "ni", "nj", "nl", "nn", "nr", "ns", "nt", "ny", "oa", "ob", "oc", "od", "of", "og", "oi", "oj", "ol", "om", "on", "oo", "oq", "or", "os", "ot", "ou", "ow", "ox", "oz", "p1", "p2", "p3", "pc", "pd", "pe", "pf", "ph", "pi", "pj", "pk", "pl", "pm", "pn", "po", "pq", "pr", "ps", "pt", "pu", "py", "qj", "qu", "r2", "ra", "rc", "rd", "rf", "rh", "ri", "rj", "rl", "rm", "rn", "ro", "rq", "rr", "rs", "rt", "ru", "rv", "ry", "s2", "sa", "sc", "sd", "se", "sf", "si", "sj", "sl", "sm", "sn", "sp", "sq", "sr", "ss", "st", "sy", "sz", "t1", "t2", "t3", "tb", "tc", "td", "te", "tf", "th", "ti", "tj", "tl", "tm", "tn", "tp", "tq", "tr", "ts", "tt", "tv", "tx", "ue", "ui", "uj", "uk", "um", "un", "uo", "ur", "ut", "va", "wa", "vd", "wi", "vj", "vo", "wo", "vq", "vt", "vu", "x1", "x2", "x3", "xf", "xi", "xj", "xk", "xl", "xn", "xo", "xs", "xt", "xv", "xx", "y2", "yj", "yl", "yr", "ys", "yt", "zi", "zz"]
stop_words_b = set(stopwords.words("english"))

keyword_dict = []

r = RAKE.Rake(RAKE.NLTKStopList())
text = ""

for plan in plans["plans"]:
    text = plan["summary"]

    rake_results = r.run(text, minCharacters=3, maxWords=4, minFrequency=1)
    key_phrases = []
    for result in rake_results:
        key_phrases.append(result[0])
    #scored_phrases = r.get_ranked_phrases()
    keyword_dict.append({"id":plan['id'], "topic": plan['display_title'], "synonym_keyphrases": key_phrases})


print(json.dumps(keyword_dict, sort_keys=False, indent=4, separators=(',', ': ')))


