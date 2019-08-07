import praw
import pdb
import re
import os
import fuzzywuzzy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#change dev to prod to shift to production bot
reddit = praw.Reddit('dev')

# Create query response dictionary
plans_dict = {
    "student debt" :            '''Senator Warren believes we should treat higher education like our public school system – free and accessible to all Americans. 
                                That’s why she's calling for something truly transformational – the cancellation of up to $50,000 in student loan debt for 
                                42 million Americans and free universal college for everyone. 
                                Learn about her plan for [Cancellation of Student Loan Debt and Universal Free Public College](https://medium.com/@teamwarren/im-calling-for-something-truly-transformational-universal-free-public-college-and-cancellation-of-a246cd0f910f).''',
    "immigration reform":       '''Immigrants are our neighbors and our friends. But an immigration system that can't tell the difference between a terrorist 
                                and a little girl is badly broken. That’s why Sen. Warren believes immigration reform must include a rules-based 
                                system that protects our security, grows our economy, and reflects our values. 
                                Learn more about her plan for [A Fair and Welcoming Immigration System](https://medium.com/@teamwarren/a-fair-and-welcoming-immigration-system-8fff69cd674e).''',
    "wall street reform":       '''For decades, Washington has lived by a simple rule: If it’s good for Wall Street, it’s good for the economy. 
                                But for a long time now, Wall Street’s success hasn’t helped the broader economy – it’s come at the expense of the rest of the economy. 
                                Sen. Warren's plan shuts down the Wall Street giveaways and reins in the financial industry so that it stops sucking money 
                                out of the rest of the economy. 
                                Learn more about her plan to [End Wall Street's Stranglehold on Our Economy](https://medium.com/@teamwarren/end-wall-streets-stranglehold-on-our-economy-70cf038bac76).''',
    "strong economy":           '''Sen. Warren rang the alarm before the 2008 financial crisis -- but Congress and regulators didn’t listen. Now she's seeing warning signs in our economy again. 
                                She believes we need to take concrete steps now to shore up our economy and reduce the risk of economic shocks if we want to reduce the chances of another crash.
                                Learn more about [The Next Economic Crash -- And How to Stop It](https://medium.com/@teamwarren/the-coming-economic-crash-and-how-to-stop-it-355703da148b).''',
    "clean green energy":       '''Climate change is real, it’s man-made, and our government needs to take bold action and use all the tools available to combat it before it’s too late. 
                                Building on some of her earlier plans to address climate change, Sen. Warren's new plan attacks it by using the power of public markets 
                                to accelerate the adoption of clean energy. 
                                Learn more about her plan to [Accelerate the Transition to Clean Energy](https://medium.com/@teamwarren/accelerating-the-transition-to-clean-energy-46af492d8c57).''',
    "pay for women of color":   '''Our economy should be working just as hard for women of color as women of color work for our economy and their families, but for decades, 
                                the government has helped perpetuate the systemic discrimination that has denied women of color fair pay and equal opportunities. 
                                That’s why Sen. Warren has a new plan: a set of executive actions she will take on day one of the Warren Administration to boost wages 
                                for women of color and open up new pathways to the leadership positions they deserve. 
                                Learn more about about Sen. Warren's plan for [Valuing the Work of Women of Color](https://medium.com/@teamwarren/valuing-the-work-of-women-of-color-c652bf6ccc9a).''',
    "diplomacy":                '''American security and prosperity depend on robust diplomacy, but Donald Trump has declared war on our State Department through a toxic combination of malice and neglect. 
                                Sen. Warren has a plan to rebuild the State Department by doubling the size of the foreign service and recruiting and retaining a bold, 
                                diverse, and professional 21st century diplomatic corps. She is also making a commitment to end the corrupt practice of selling cushy 
                                diplomatic posts to wealthy donors. She won’t give ambassadorial posts to wealthy donors or bundlers -- and she's calling on everyone running for 
                                President to do the same. 
                                Learn more about her plan for [Revitalizing Diplomacy: A 21st Century Foreign Service](https://medium.com/@teamwarren/revitalizing-diplomacy-a-21st-century-foreign-service-2d9d195698f).''',
    "election reform":          '''It’s time to make voting easy and convenient, stop racist voter suppression, and secure our elections. 
                                Sen. Warren's plan creates uniform federal rules to make voting easy for everyone - no registration problems, no purges, no difficulties voting, 
                                and no gerrymandering - and we’ll have federal funding to make sure our elections are secure from hacking. 
                                Learn more about [Her Plan to Strengthen Our Democracy](https://medium.com/@teamwarren/my-plan-to-strengthen-our-democracy-6867ec1bcd3c).''',
    "for profit prison reform": '''Washington hands billions over to private prison and detention companies that profit off of inhumane detention and incarceration policies. 
                                That stops now. Sen. Warren's plan will root out the profit interests standing in the way of real reform by banning privately-owned facilities 
                                and preventing companies from exploiting those caught in our criminal and immigration systems. 
                                Learn more about her plan for [Ending Private Prisons  and Exploitation for Profit](https://medium.com/@teamwarren/ending-private-prisons-and-exploitation-for-profit-cb6dea67e913).''',
    "minority business owners": '''Generations of government discrimination have denied Black and other minority families opportunities to build wealth, making it harder for them to start a successful 
                                business and holding back our economy. Sen. Warren's new plan provides $7 billion in funding to help level the playing field, and support 100,000 small businesses and more than a million jobs.
                                Learn more about her plan for [Leveling the Playing Field for Entrepreneurs](https://medium.com/@teamwarren/leveling-the-playing-field-for-entrepreneurs-2a585aa2b6d7).''',
    "create American jobs":     '''For decades, we’ve let giant corporations run our economy even though they have no loyalty or allegiance to America. 
                                Not on her watch. She will use all the tools of government to defend and create good American jobs. 
                                Learn more about her plan for [The New American Patriotism](https://medium.com/@teamwarren/a-plan-for-economic-patriotism-13b879f4cfc7).''',
    "green energy jobs":        '''By investing $2 trillion in American research and American manufacturing of clean energy technology, 
                                we can lead the global effort to combat climate change, boost our economy, and create more than a million good jobs here at home. 
                                Learn more about her [Green Manufacturing Plan](https://medium.com/@teamwarren/my-green-manufacturing-plan-for-america-fc0ad53ab614).''',
    "crimes by the president":  '''Impeachment isn’t supposed to be the only way that a President can be held accountable for committing a crime. 
                                Congress should make it clear that Presidents can be indicted for criminal activity, including obstruction of justice. 
                                And when she's President, she'll appoint Justice Department officials who will reverse flawed policies so no President is shielded from criminal accountability.
                                Learn more about her [Plan to Make Sure That No President is Above the Law](https://medium.com/@teamwarren/no-president-is-above-the-law-f4812e580336).''',
    "reproductive rights":      '''Our democracy should not be held hostage by right-wing courts, and women should not have to hope that Brett Kavanaugh and Donald Trump's Supreme Court 
                                will respect the law. Congress should pass new federal laws that protect access to reproductive care from right-wing ideologues in the states. 
                                Federal laws that ensure real access to birth control and abortion care for all women. Federal laws that will stand no matter what the Supreme Court does.
                                Learn more about her plan for [Congressional Action to Protect Choice](https://medium.com/@teamwarren/congressional-action-to-protect-choice-aaf94ed25fb5).''',
    "military lobbyists":       '''The revolving door between defense lobbyists, Congress, and the Pentagon tilts countless decisions away from legitimate national security interests and toward 
                                the desires of giant defense contractors. It’s past time to cut our bloated defense budget – and to get serious about cutting defense spending, 
                                we need to reduce corporate influence. Americans deserve to know that our military is making decisions with only one thing in mind: their safety. 
                                That's why Sen. Warren plans to slam shut the revolving door and curb the influence of giant defense contractors on the Pentagon. 
                                Learn more about her plan to [Reduce Corporate Influence at the Pentagon](https://medium.com/@teamwarren/its-time-to-reduce-corporate-influence-at-the-pentagon-98f52ee0fcf1).''',
    "climate change security":  '''Climate change is real, it is worsening by the day, and it is undermining our military readiness. But instead of meeting this threat head-on, 
                                Washington is ignoring it – and making it worse. Senator Warren has a plan to make the U.S. military more resilient to climate change, 
                                and to leverage its huge energy footprint as part of our climate solution. Her energy and climate resiliency plan will improve our service members’ 
                                readiness and safety, all while achieving cost savings for American taxpayers. 
                                Learn more about her plan for [National Security & Climate Change](https://medium.com/@teamwarren/our-military-can-help-lead-the-fight-in-combating-climate-change-2955003555a3).''',
    "Opioid Crisis":            '''Every day, 130 Americans die from an opioid overdose. This is a public health crisis – and we need to start treating it like one. 
                                That's why Congressman Elijah Cummings and Senator Warren introduced the CARE Act, a comprehensive plan that invests $100 billion over the next 
                                ten years in states and communities that are on the frontlines of the epidemic - to provide prevention, treatment, and recovery services 
                                for those who need it most. 
                                Learn more about her plan for [Tackling the Opioid Crisis Head On](https://medium.com/@teamwarren/my-comprehensive-plan-to-end-the-opioid-crisis-9d85deaa3ccb).''',
    "Puerto Rico debt relief":  '''After Hurricanes Irma and Maria devastated Puerto Rico, one of the biggest constraints holding back the island's recovery has been its debt. 
                                If Puerto Rico were a big company or an American city, it could file for bankruptcy, but because of its unique status, those legal options 
                                aren’t available. That’s why Sen. Warren has a plan to provide comprehensive debt relief to Puerto Rico so it can rebuild and thrive. 
                                Learn more about her plan [To Provide Debt Relief for Puerto Rico](https://medium.com/@teamwarren/my-plan-to-provide-comprehensive-debt-relief-to-puerto-rico-f8b575a81b06).''',
    "maternal mortality":       '''We are facing a maternal mortality crisis in America. And for Black moms, it's an epidemic. One major reason? Racism. 
                                It's time to hold health systems accountable for preventable failures and demand change – because women's lives depend on it. 
                                Learn more about her plan for [Addressing Our Maternal Mortality Epidemic](https://www.essence.com/feature/sen-elizabeth-warren-black-women-mortality-essence/).''',
    "improve military housing": '''Our military families have been raising the alarm about their living conditions for years. This stops now. Sen. Warren has a plan to improve 
                                our military housing, protect families from abuse, and hold private developers accountable for the promises they make to those who serve our country.
                                Learn more about her plan [To Improve Our Military Housing](https://medium.com/@teamwarren/my-plan-to-improve-our-military-housing-b1a46ba235b8).''',
    "public land":              '''Sen. Warren is making a promise. On the first day of her administration, she will sign a moratorium so that there is no more drilling on public lands, 
                                and she will set a goal of providing 10 percent of our overall electricity generation from renewable sources. Climate change is here, it is real, 
                                and we should make our public lands part of the solution. 
                                Learn more about her [Plan for Public Lands](https://medium.com/@teamwarren/my-plan-for-public-lands-e4be1d88a01c).''',
    "corporate taxes":          '''Year after year, some of the biggest corporations in the country make huge profits, but pay zero federal corporate income taxes on those profits. 
                                That isn’t right. Sen. Warren's Real Corporate Profits Tax will raise over a trillion dollars and make sure the biggest corporations pay their fair share.
                                Learn more about her plan for a [Real Corporate Profits Tax](https://medium.com/@teamwarren/im-proposing-a-big-new-idea-the-real-corporate-profits-tax-29dde7c960d).''',
    "ceo accountability":       '''Our justice system should ensure that if you cheat working Americans, you’ll go to jail. It’s time to reform our laws to make sure that corporate 
                                executives are held accountable for overseeing massive scams. 
                                Learn more about Sen. Warren's [Corporate Executive Accountability Act](https://www.washingtonpost.com/opinions/elizabeth-warren-its-time-to-scare-corporate-america-straight/2019/04/02/ca464ab0-5559-11e9-8ef3-fbd41a2ce4d5_story.html).''',
    "family farmers":           '''Today, a farmer can work hard, do everything right, and still not make it. Sen. Warren's plan gives family farmers a fair shot by tackling consolidation, 
                                un-rigging the rules that favor big agribusiness, and standing up for America’s farmers against foreign interests. 
                                Learn more about her plan for [Leveling the Playing Field for America's Family Farmers](https://medium.com/@teamwarren/leveling-the-playing-field-for-americas-family-farmers-823d1994f067).''',
    "electoral college":        '''Presidential candidates should have to ask every American in every part of the country for their vote. We can make that happen by abolishing the 
                                Electoral College and replacing it with a national popular vote. 
                                Learn more about Sen. Warren's plan [To Get Rid of the Electoral College](https://medium.com/@teamwarren/its-time-to-get-rid-of-the-electoral-college-20efcac09c5e).''',
    "safe affordable housing":  '''Every American deserves a safe and affordable place to live. Sen. Warren's plan makes a historic investment in housing that would bring 
                                down rents by 10%, create 1.5 million new jobs, and begin closing the racial wealth gap. 
                                Learn more about her [Housing Plan for America](https://medium.com/@teamwarren/my-housing-plan-for-america-20038e19dc26).''',
    "big tech companies":       '''America’s biggest tech companies are controlling more and more of our digital lives and using their size and power to make it harder for the next tech 
                                entrepreneur with the next big idea to compete. It’s time to break up the biggest tech companies to restore competition – and make sure these corporations 
                                don’t get so powerful that they undermine our democracy. 
                                Learn more about Sen. Warren's plan for [How We Can Break Up Big Tech](https://medium.com/@teamwarren/heres-how-we-can-break-up-big-tech-9ad9e0da324c).''',
    "universal child care":     '''We’re the wealthiest country on the planet – high-quality child care and early education shouldn’t be a privilege that’s only for the rich. 
                                Sen. Warren is fighting to make high-quality child care from birth to school age free for millions of families and affordable for all. 
                                Learn more about her [Plan for Universal Child Care](https://medium.com/@teamwarren/my-plan-for-universal-child-care-762535e6c20a).''',
    "ultra millionaire tax":    '''Sen. Warren is proposing something brand new – a tax on the wealth of the richest Americans. My Ultra-Millionaire Tax asks America's richest 0.1% to pay their 
                                fair share, raising nearly $3 trillion that we can use to rebuild the middle class. 
                                Learn more about her plan for [The Ultra-Millionaire Tax](https://elizabethwarren.com/ultra-millionaire-tax/).''',
}

# init topic keyword array
query_terms = []

for key in plans_dict:
    query_terms.append(key)

# Check if replied posts exists, if not create an empty list
if not os.path.isfile("posts_replied_to.txt"):
    posts_replied_to = []

# If replied posts file exists, load the list of posts replied to from it
else:
    # Read the file into a list and remove any empty values
    with open("posts_replied_to.txt", "r") as f:
        posts_replied_to = f.read()
        posts_replied_to = posts_replied_to.split("\n")
        posts_replied_to = list(filter(None, posts_replied_to))

# Get the subreddit
subreddit = reddit.subreddit("WPBSandbox")

# Set const for number of posts to return
post_limit = 10

# Get the number of new posts up to the limit
for submission in subreddit.new(limit=post_limit):
    submission_ID = submission.id
    
    # If we haven't replied to this post before
    if submission.id not in posts_replied_to:

        # Do a case insensitive search
        if re.search("!warrenplanbot | /u/WarrenPlanBot", submission.selftext, re.IGNORECASE):
            # Log Submission Data
            print("submission id: ", submission.id)
            print("submission text: ", submission.selftext)
            
            # Search topic keywords and response body for best match
            topic_match_in_post = process.extractOne(submission.selftext, query_terms, scorer=fuzz.WRatio)
            print("topic found in post text: ", topic_match_in_post[0])
            print("topic found in post confidence: ", topic_match_in_post[1])

            # Reply to the post with plan info, uncomment next line to activate post replies
            submission.reply(plans_dict[topic_match_in_post[0]]) 
            print("Bot replying to: ", submission.title)
            posts_replied_to.append(submission.id)
        
        # After checking submission.selftext, check comments
        # Get comments for submission and search for trigger in comment body
        submission.comments.replace_more(limit=None)
        for comment in submission.comments.list():
            # If we haven't replied to the comment before
            if comment.id not in posts_replied_to:
                # Log Comment Data
                print("comment id: ", comment.id)
                print("comment text: ", comment.body)

                # Search for trigger phrases in the comment
                if re.search("!warrenplanbot | /u/warrenplanbot", comment.body, re.IGNORECASE):

                    # Search for matching topic keywords in comment body
                    topic_match_in_comments = process.extractOne(comment.body, query_terms, scorer=fuzz.WRatio)
                    print("topic found in comment ID", comment.id)
                    print("topic found in comment: ", topic_match_in_comments[0])
                    print("topic found in comments confidence: ", topic_match_in_comments[1])
                    
                    comment.reply(plans_dict[topic_match_in_comments[0]]) 
                    print("Bot replying to: ", comment.id)
                    posts_replied_to.append(comment.id)

# Write the updated list back to the file
with open("posts_replied_to.txt", "w") as f:
    for post_id in posts_replied_to:
        # uncomment next line when ready to start recording post IDs so it doesn't reply multiple times
        f.write(post_id + "\n")
        print("replied to : ", post_id + "\n")

