import os
from os import path
import csv
import re
from statistics import stdev
import spacy
import json
import sys
import shutil
from operator import itemgetter


#Fetches the whole_text from the PHP POST method.
whole_text = sys.argv[1].replace("\?", "?").replace('\"', '"').replace("\;", ";").replace("\(", "(").replace("\)", ")").replace("\&", "&").replace("\+", "+").replace("\*", "*").replace("\[", "[").replace("\]", "]").replace("\{", "{").replace("\}", "}").replace("\$", "$").replace("\=", "=").replace("\!", "!").replace("\^", "^").replace("\<", "<").replace("\>", ">").replace("\|", "|").replace("\:", ":").replace("\-", "-").replace("\/", "/")

#The English accent (British vs US-English) will determine which heteronyms list is used for the substitution of the Speech Synthesis Markup Language (SSML) "phoneme" tags for their corresponding
#heteronyms. This will have an impact on which heteronums get their pronounciation altered (such as "address", which is pronounced the same in British English whether it is a noun or a verb,
#but is pronounced differently for these two parts of speech in American English). "English_Phonetics" defaults to American_English if the user didn't select a English accent value.
if len(sys.argv)>2:
    English_Phonetics = sys.argv[2]
else:
    English_Phonetics = "American_English"

cwd = os.getcwd()

#The order is of heteronyms in the lists is important here. For example: 'bows' needs to be substituted before 'bow', in order to avoid mixups.
#Having 'bow' before 'bows' in the lists would lead to 'bows' being converted to 'bough' and 'bow' instead of 'boughs' and 'bose',
#as 'bow' is found in 'bows'.

heteronyms_list_American_English = ["Absent", "Abstract", "Abuse", "Acuminate", "Addict", "Adduct", "Adept", "Adulterate", "Advert", "Advocate", "Affect", "Affiliate", "Agglomerate", "Agglutinate", "Aggregate", "Aliment", "Allied", "Alloy", "Ally", "Alternate", "Analyses", "Animate", "Annex", "Appropriate", "Approximate", "Arithmetic", "Articulate", "Aspirate", "Associate", "Attribute", "Augment", "August", "Axes", "Bases", "Blessed", "Bows", "Bow", "Buffet", "Certificate", "Chassis", "Close", "Coagulate", "Coax", "Collect", "Combat", "Combine", "Commune", "Compact", "Complex", "Compound", "Compress", "Concert", "Concrete", "Conduct", "Confect", "Confines", "Conflict", "Conglomerate", "Congress", "Conjugate", "Conscript", "Conserve", "Console", "Consociate", "Consort", "Consummate", "Construct", "Content", "Contest", "Contract", "Contrast", "Converse", "Convert", "Convict", "Coordinate", "Co-ordinate", "Crooked", "Decrease", "Defect", "Degenerate", "Delegate", "Deliberate", "Derogate", "Desert", "Desolate", "Deviate", "Diagnoses", "Diffuse", "Digest", "Dingy", "Discard", "Discharge", "Discord", "Discount", "Do", "Does", "Dogged", "Dove", "Duplicate", "Egress", "Ejaculate", "Elaborate", "Ellipses", "Entrance", "Envelop", "Escort", "Essay", "Estimate", "Excuse",  "Exploit", "Extract", "Ferment", "Frequent", "Graduate", "Hinder", "House", "Implant", "Import", "Impress", "Imprint", "Incense", "Incline", "Incorporate", "Increase", "Indent", "Initiate", "Insert", "Inset", "Instinct", "Insult", "Intercept", "Intermediate", "Intern", "Intimate", "Invite", "Isolate", "Jagged", "Lead", "Learned", "Legitimate", "Lied", "Live", "Lower", "Lupine", "Merchandise", "Minute", "Misconduct", "Misread", "Mobile", "Moderate", "Moped", "Mouse", "Mouth", "Mow", "Multiply", "Number", "Object", "Obligate", "Overage", "Overall", "Overhead", "Overlook", "Overrun", "Pedal", "Perfect", "Permit", "Pervert", "Polish", "Postulate", "Precedent", "Precipitate", "Predicate", "Premise", "Present", "Proceeds", "Produce", "Progress", "Project", "Proofread", "Protest", "Pussy", "Putting", "Raven", "Read", "Rebel", "Recall", "Recap", "Recess",  "Recoil", "Recollect", "Record", "Redress", "Refill", "Refit", "Reflex", "Refund", "Refuse", "Regenerate", "Regress", "Rehash", "Reject", "Relapse", "Relay", "Remake", "Repatriate", "Repent", "Replay", "Reprint", "Rerun", "Retake", "Retard", "Rewind", "Segment", "Separate", "Skied", "Sow", "Stabile", "Stipulate", "Subject", "Supply", "Supposed", "Survey", "Suspect", "Syndicate", "Tarry", "Tear", "Torment", "Transect", "Transplant", "Transport", "Upset", "Use", "Used", "Wicked", "Wind", "Wound"]

heteronyms_list_British_English = ["Absent", "Abstract", "Abuse", "Accent", "Acuminate", "Addict", "Adduct", "Adept", "Adulterate", "Advert", "Advocate", "Affect", "Affiliate", "Agglomerate", "Agglutinate", "Aggregate", "Aliment", "Allied", "Alloy", "Ally", "Alternate", "Analyses", "Animate", "Annex", "Appropriate", "Approximate", "Arithmetic", "Articulate", "Aspirate", "Associate", "Attribute", "Augment", "August", "Axes", "Bases", "Bows", "Blessed", "Bow", "Buffet", "Certificate", "Chassis", "Close", "Coagulate", "Coax", "Collect", "Combat", "Combine", "Commune", "Compact", "Compound", "Compress", "Concert", "Conduct", "Confect", "Confines", "Conflict", "Conglomerate", "Congress", "Conjugate", "Conscript", "Console", "Consociate", "Consort", "Consummate", "Construct", "Content", "Contest", "Contract", "Contrast", "Converse", "Convert", "Convict", "Coordinate", "Co-ordinate", "Crooked", "Decrease", "Defect", "Degenerate", "Deliberate", "Derogate", "Desert", "Desolate", "Deviate", "Diagnoses", "Diffuse", "Digest", "Dingy", "Discard", "Discharge", "Discord", "Discount", "Do", "Does", "Dogged", "Dove", "Duplicate", "Egress", "Ejaculate", "Elaborate", "Ellipses", "Entrance", "Envelop", "Escort", "Essay", "Estimate", "Excise", "Excuse", "Exploit", "Extract", "Ferment", "Frequent", "Graduate", "Hinder", "House", "Implant", "Import", "Impress", "Imprint", "Incense", "Incline", "Incorporate", "Increase", "Indent", "Initiate", "Insert", "Inset", "Instinct", "Insult", "Intercept", "Intermediate", "Intern", "Intimate", "Invite", "Involute", "Isolate", "Jagged", "Lead", "Learned", "Legitimate", "Lied", "Live", "Lower", "Lupine", "Merchandise", "Minute", "Misconduct", "Misread", "Mobile", "Moderate", "Moped", "Mouse", "Mouth", "Mow", "Multiply", "Number", "Object", "Overage", "Overall", "Overhead", "Overlook", "Overrun", "Pedal", "Perfect", "Permit", "Pervert", "Polish", "Postulate", "Precedent", "Precipitate", "Predicate", "Premise", "Present", "Proceeds", "Produce", "Progress", "Project", "Proofread", "Prospect", "Protest", "Pussy", "Putting", "Raven", "Read", "Rebel", "Recall", "Recap", "Recess", "Recitative", "Recoil", "Recollect", "Record", "Refill", "Refit", "Reflex", "Refund", "Refuse", "Regenerate", "Regress", "Rehash", "Reject", "Relapse", "Relay", "Remake", "Repatriate", "Repent", "Replay", "Reprint", "Rerun", "Retake", "Retard", "Rewind", "Segment", "Separate", "Skied", "Sow", "Stipulate", "Subject", "Supply", "Supposed", "Survey", "Suspect", "Syndicate", "Tarry", "Tear", "Torment", "Transect", "Transfer", "Transplant", "Transport", "Upset", "Use", "Used", "Wicked", "Wind", "Wound"]

onomatopoeias = ["[^\w]Achoo[^\w]", "[^\w]Arg[h]+[^\w]", "[^\w]Br[r]+ng[^\w]", "[^\w]BR[R]+[^\w]", "[^\w]Br[r]+[^\w]", "[^\w]Bz[z]+[^\w]", "[^\w]Ca-ching[^\w]", "[^\w]Chaching[^\w]", "[^\w]Ka-ching[^\w]", "[^\w]Kerching[^\w]", "[^\w]Ca-chunk[^\w]", "[^\w]Ka-chunk[^\w]", "[^\w]G-R[-R]+[^\w]", "[^\w]G-r[-r]+[^\w]", "[^\w]GR[R]+[^\w]", "[^\w]Gr[r]+[^\w]", "[^\w]Pizzaz[^\w]", "[^\w]Ps[s]+t[^\w]", "[^\w]Sh[h]+[^\w]", "[^\w]T[s]+k[^\w]", "[^\w]Ug[h]+[^\w]", "[^\w]Yip pee[^\w]", "[^\w]Yippee[^\w]", "[^\w]Zz[z]+[^\w]", "[^\w]Pshaw[^\w]"]
modified_onomatopoeias = ['<phoneme alphabet="ipa" ph="əˈt͡ʃuː">Achoo</phoneme>', '<phoneme alphabet="ipa" ph="ɑːx">Argh</phoneme>', '<phoneme alphabet="ipa" ph="ˈbriŋ">Ring</phoneme>', '<phoneme alphabet="ipa" ph="bɜr">Shiver</phoneme>', '<phoneme alphabet="ipa" ph="bɜr">Shiver</phoneme>', '<phoneme alphabet="ipa" ph="bʌz">Buzz</phoneme>', '<phoneme alphabet="ipa" ph="tʃəˈtʃɪŋ">Ca-ching</phoneme>', '<phoneme alphabet="ipa" ph="tʃəˈtʃɪŋ">Chaching</phoneme>', '<phoneme alphabet="ipa" ph="tʃəˈtʃɪŋ">Ka-ching</phoneme>', '<phoneme alphabet="ipa" ph="tʃəˈtʃɪŋ">Kerching</phoneme>', '<phoneme alphabet="ipa" ph="ˈkəchəŋk">Ca-chunk</phoneme>', '<phoneme alphabet="ipa" ph="ˈkəchəŋk">Ka-chunk</phoneme>', '<phoneme alphabet="ipa" ph="ˈgər">Growl</phoneme>', '<phoneme alphabet="ipa" ph="ˈgər">Growl</phoneme>', '<phoneme alphabet="ipa" ph="ˈgər">Growl</phoneme>', '<phoneme alphabet="ipa" ph="ˈgər">Growl</phoneme>', '<phoneme alphabet="ipa" ph="pɪzæz">Pizzaz</phoneme>', '<phoneme alphabet="ipa" ph="pst">Hist</phoneme>', '<phoneme alphabet="ipa" ph="ʃ">Shush</phoneme>', '<phoneme alphabet="ipa" ph="tɪsk">Tisk</phoneme>', '<phoneme alphabet="ipa" ph="ʊːx">Ugh</phoneme>', '<phoneme alphabet="ipa" ph="jɪpiː">Yip pee</phoneme>', '<phoneme alphabet="ipa" ph="jɪpiː">Yippee</phoneme>', '<phoneme alphabet="ipa" ph="ziːz">Snore</phoneme>', '<phoneme alphabet="ipa" ph="ʃɔ">Pshaw</phoneme>']

hyphens = [' --', ' —', '-- ', '— ' , ' -- ', ' — ', '--', '—']

#Since in some cases I am adding a comma on both sides of the phrase, I thus include [^\w] on both sides of the phrase, in the event that there is aldready a comma in these locations. I know [^\w] is not strictly needed on the left side, and that in theory a space could preclude inclusion of words containing such suffixes, but better safe than sorry in the event that there is a comma right next to the word (ex: ",admittedly") and where I want to add a comma on either side of the phrase.
linking_words_middle_of_sentence_no_comma = ["[^\w]admittedly[^\w]", "[^\w]as a result of[^\w]", "[^\w]as a result[^\w]", "[^\w]but[^\w]", ", but one[^\w]", "[^\w]by the way[^\w]", "[^\w]despite the[^\w]", "[^\w]for example[^\w]", "[^\w]for instance[^\w]", "[^\w]hence[^\w]", "[^\w]in addition[^\w]", "[^\w]in spite of[^\w]", "[^\w]in the same way[^\w]", "[^\w]including[^\w]", "[^\w]indeed[^\w]", "[^\w]moreover[^\w]", "[^\w]namely[^\w]", "[^\w]nor[^\w]", "[^\w]on the contrary[^\w]", "[^\w]on the one hand[^\w]", "[^\w]on the other hand[^\w]", "[^\w]as a consequence[^\w]", "[^\w]which indeed[^\w]"]
linking_words_middle_of_sentence_with_comma = [", admittedly, ", ", as a result of ", ", as a result, ", ", but ", " but one ", ", by the way, ", ", despite the ", ", for example, ", ", for instance, ", ", hence ", ", in addition ", ", in spite of ", ", in the same way, ", ", including ", ", indeed, ", ", moreover, ", ", namely ", ", nor ", ", on the contrary, ", ", on the one hand, ", ", on the other hand, ", "as a consequence, ", ", which indeed "]

but_middle_of_sentence_comma_inside = ["[^\w]all, but[^\w]", "[^\w]anything, but[^\w]", "[^\w]can.t, but[^\w]", "[^\w]cannot, but[^\w]", "[^\w]everything, but[^\w]", "[^\w]is, but[^\w]", "[^\w]last, but not least[^\w]", "[^\w]none, but[^\w]", "[^\w]nothing, but[^\w]", "[^\w]sad, but true[^\w]", "[^\w]slow, but sure[^\w]", "[^\w]slowly, but surely[^\w]", "[^\w]was, but[^\w]"]
but_middle_of_sentence_no_comma = [" all but ", " anything but ", " can.t but ", " cannot but ", " everything but ", " is but ", " last but not least, ", " none but ", " nothing but ", " sad but true ", " slow but sure ", " slowly but surely ", " was but "]

linking_words_start_of_sentence_no_comma = ["Additionally ", "Admittedly ", "As a consequence ", "As a result ", "Besides ", "But ", "By the way ", "Consequently ", "Conversely ", "Firstly ", "For example ", "For instance ", "Furthermore ", "Hence ", "Importantly ", "In addition ", "In conclusion ", "In spite of this ", "In spite of that ", "In the same way ", "Indeed ", "Moreover ", "Namely ", "Nevertheless ", "Nonetheless ", "On the contrary ", "On the one hand ", "On the other hand ", "Secondly ", "Similarly ", "Specifically ", "Subsequently ", "Therefore ", "Thus "]
linking_words_start_of_sentence_with_comma = ["Additionally, ", "Admittedly, ", "As a consequence, ", "As a result, ", "Besides, ", "But, ", "By the way, ", "Consequently, ", "Conversely, ", "Firstly, ", "For example, ", "For instance, ", "Furthermore, ", "Hence, ", "Importantly, ", "In addition, ", "In conclusion, ", "In spite of this, ", "In spite of that, ", "In the same way, ", "Indeed, ", "Moreover, ", "Namely, ", "Nevertheless, ", "Nonetheless, ", "On the contrary, ", "On the one hand, ", "On the other hand, ", "Secondly, ", "Similarly, ", "Specifically, ", "Subsequently, ", "Therefore, ", "Thus, "]

yet_comma_inside_capitalized = ["And, yet", "Anything, yet", "As of, yet", "As, yet", "Better, yet", "But, yet", "Can[.]t, yet", "Cannot, yet", "From, yet", "He, yet", "I, yet", "Just, yet", "May, yet", "Might, yet", "Never, yet", "Not just, yet", "Not, yet", "Nothing, yet", "Of, yet", "She, yet", "They, yet", "We, yet", "Worse, yet"]
yet_no_comma_capitalized = ["And yet, ", "Anything yet", "As of yet, ", "As yet, ", "Better yet, ", "But yet", "Can[.]t yet", "Cannot yet", "From yet", "He yet", "I yet", "Just yet", "May yet", "Might yet", "Never yet", "Not just yet", "Not yet", "Nothing yet", "Of yet", "She yet", "They yet", "We yet", "Worse yet"]

#I do not put [^\w] on the right side of 'yet', only instances of ' yet ' have been replaced by ', yet ' to begin with (the same logic applies for the other phrases such as 'which'). I do not put a space on the right side of 'yet', as I want to include results already having a comma in that position. This is important, as I am removing superfluous inside commas from all phrases, whether or not they have a comma on the right side. I know [^\w] is not strictly needed on the left side, and that in theory a space could preclude inclusion of words containing such suffixes, but better safe than sorry in the event that there is a comma right next to the word (ex: ",anything, yet").
yet_comma_inside_lowercase = ["[^\w]anything, yet", "[^\w]are, yet", "[^\w]aren[.]t, yet", "[^\w]arrived, yet", "[^\w]as of, yet", "[^\w]as, yet", "[^\w]better, yet", "[^\w]but, yet", "[^\w]can[.]t, yet", "[^\w]cannot, yet", "[^\w]come, yet", "[^\w]did, yet", "[^\w]didn[.]t, yet", "[^\w]doesn[.]t, yet", "[^\w]don[.]t, yet", "[^\w]from, yet", "[^\w]had, yet", "[^\w]hadn[.]t, yet", "[^\w]has, yet", "[^\w]hasn[.]t, yet", "[^\w]he, yet", "[^\w]is, yet", "[^\w]just, yet", "[^\w]may, yet", "[^\w]might, yet", "[^\w]never, yet", "[^\w]not just, yet", "[^\w]not, yet", "[^\w]nothing, yet", "[^\w]of, yet", "[^\w]over, yet", "[^\w]quite, yet", "[^\w]seemed, yet", "[^\w]she, yet", "[^\w]they, yet", "[^\w]was, yet", "[^\w]wasn[.]t, yet", "[^\w]we, yet", "[^\w]were, yet", "[^\w]weren[.]t, yet", "[^\w]worse, yet", "[^\w]and, yet"]
yet_no_comma_lowercase = [" anything yet", " are yet", " aren[.]t yet", " arrived yet", " as of yet", " as yet", " better yet, ", " but yet", " can[.]t yet", " cannot yet", " come yet", " did yet", " didn[.]t yet", " doesn[.]t yet", " don[.]t yet", " from yet", " had yet", " hadn[.]t yet", " has yet", " hasn[.]t yet", " he yet", " is yet", " just yet", " may yet", " might yet", " never yet", " not just yet", " not yet", " nothing yet", " of yet", " over yet", " quite yet", " seemed yet", " she yet", " they yet", " was yet", " wasn[.]t yet", " we yet", " were yet", " weren[.]t yet", " worse yet", ", and yet"]

#I have the 'or' phrases capitalized, since I add a comma after 'believe it or not', 'sooner or later' and after 'for better or for worse', which could be at the beginning of the sentence (I do the substitutions for the capitalized and lower case versions of the phrases).
or_comma_inside = ["A thing, or two", "All, or none", "All, or nothing", "Believe it, or not", "Better, or for worse", "Better, or worse", "Black, or white", "Coming, or going", "Common, or garden", "Covered, or hedge", "Dead, or alive", "Deficit, or surplus", "Dick, or Harry", "Do, or die", "Double, or nothing", "Eight, or nine", "Either, or", "Feast, or famine", "Fight, or flight", "Fill, or kill", "Fish, or cut bait", "Five, or six", "For better, or for worse", "Four, or five", "Free, or die", "Friend, or foe", "Give, or take", "Head, or tail", "Heads, or tails", "Hell, or high water", "Hit, or miss", "Hook, or by crook", "Hook, or crook", "Kill, or cure", "Life, or death", "Like it, or lump it", "Like it, or not", "Little, or no", "Little, or none", "Love, or money", "Make, or break", "May, or may not", "Means, or foul", "More, or less", "Neck, or nothing", "Nine, or ten", "On, or about", "Once, or twice", "One, or another", "One, or more", "One, or other", "One, or the other", "One, or two", "One way, or another", "One way, or the other", "Out, or keeping", "Piss, or get off the pot", "Plus, or minus", "Put up, or shut up", "Rain, or shine", "Rhyme, or reason", "Sale, or return", "Seven, or eight", "Shape, or form", "Shape up, or ship out", "Shit, or get off the pot", "Sink, or swim", "Sinks, or swim", "Six, or seven", "Somehow, or other", "Something, or other", "Sooner, or later", "Sunk, or swim", "Take it, or leave it", "Thing, or two", "Three, or four", "Three, or more", "Trick, or treat", "Trick, or treater", "Trick, or treating", "Truth, or consequences", "Truth, or dare", "Two, or more", "Two, or three", "Whether, or no", "Win, or lose"]
or_no_comma = ["A thing or two", "All or none", "All or nothing", "Believe it or not, ", "Better or for worse", "Better or worse", "Black or white", "Coming or going", "Common or garden", "Covered or hedge", "Dead or alive", "Deficit or surplus", "Dick or Harry", "Do or die", "Double or nothing", "Eight or nine", "Either or", "Feast or famine", "Fight or flight", "Fill or kill", "Fish or cut bait", "Five or six", "For better or for worse, ", "Four or five", "Free or die", "Friend or foe", "Give or take", "Head or tail", "Heads or tails", "Hell or high water", "Hit or miss", "Hook or by crook", "Hook or crook", "Kill or cure", "Life or death", "Like it or lump it", "Like it or not", "Little or no", "Little or none", "Love or money", "Make or break", "May or may not", "Means or foul", "More or less", "Neck or nothing", "Nine or ten", "On or about", "Once or twice", "One or another", "One or more", "One or other", "One or the other", "One or two", "One way or another", "One way or the other", "Out or keeping", "Piss or get off the pot", "Plus or minus", "Put up or shut up", "Rain or shine", "Rhyme or reason", "Sale or return", "Seven or eight", "Shape or form", "Shape up or ship out", "Shit or get off the pot", "Sink or swim", "Sinks or swim", "Six or seven", "Somehow or other", "Something or other", "Sooner or later, ", "Sunk or swim", "Take it or leave it", "Thing or two", "Three or four", "Three or more", "Trick or treat", "Trick or treater", "Trick or treating", "Truth or consequences", "Truth or dare", "Two or more", "Two or three", "Whether or no", "Win or lose"]

#Since there are so many phrases for or, and because some of them might be at the beginning of a sentence, I didn't bother including [^\w] on either side of the phrases
and_comma_inside = ["A, and B", "Adam, and Eve", ", and a half", ", and a third", ", and eighty", ", and fifty", ", and five", ", and forty", ", and ninety", ", and ninety five", ", and ninety nine", ", and seventy", ", and sixty", ", and ten", ", and thirty", ", and three quarters", ", and twenty", "B, and B", "Bonnie, and Clyde", "East, and West", "Herb, and Al", "Jekyll, and Hyde", "Netflix, and chill", "North, and South", "Sam, and Dave", "Siegfried, and Roy", "Stars, and Stripes", "Summer, and Winter", "a boon, and a bane", "a day late, and a dollar short", "about, and scatter", "above, and beyond", "acres, and a mule", "act, and deed", "again, and again", "aid, and abet", "airs, and graces", "alarms, and excursions", "alarums, and excursions", "alive, and kicking", "all, and end", "all, and some", "all, and sundry", "all day, and every", "all gas, and gaiters", "all hat, and no cattle", "alpha, and omega", "apples, and oranges", "arm, and a leg", "armed, and dangerous", "around, and around", "art, and part of", "arts, and crafts", "assholes, and elbows", "at sixes, and sevens", "back, and edge", "back, and fill", "back, and forth", "back, and sides", "backward, and forward", "backwards, and forwards", "bait, and switch", "ball, and chain", "ball, and run", "balls, and strikes", "bam, and scram", "banana, and split", "bark, and no bite", "beck, and call", "bed, and board", "bed, and breakfast", "bee, and buzz", "been, and done", "beer, and skittles", "before, and after", "bells, and buckets", "bells, and whistles", "belt, and braces", "bib, and tucker", "big, and bold", "binge, and purge", "birds, and the bees", "bitch, and moan", "bits, and bobs", "bits, and pieces", "bitter, and twisted", "black, and blue", "black, and tan", "black, and white", "blink, and you", "block, and tackle", "blood, and guts", "blood, and iron", "blood, and thunder", "blue, and white", "blues, and twos", "bob, and weave", "body, and soul", "boots, and all", "born, and bred", "born, and raised", "bottle, and glass", "bound, and determined", "bow, and scrape", "boys, and girls", "boys, and their toys", "brains, and brawn", "brawn, and no brain", "bread, and butter", "bread, and water", "break down, and cry", "breaking, and entering", "brick, and mortar", "bricks, and mortar", "bright, and breezy", "bright-eyed, and bushy-tailed", "bruised, and battered", "buckle, and tongue", "bull, and cow", "burning, and no ship", "by, and by", "by, and large", "bye, and good", "cake, and eat", "cake, and have it", "cakes, and ale", "cap, and bells", "carrot, and stick", "carrot, and the stick", "cash, and carry", "cat, and dog", "cat, and mouse", "cats, and dogs", "cause, and effect", "chalk, and cheese", "chapter, and verse", "checks, and balances", "chicken, and egg", "children, and drunken", "children, and fools", "chili, and beans", "chip, and dip", "chop, and charge", "cloak, and dagger", "close, and personal", "close down, and shut down", "coach, and horses", "coat, and no knickers", "coat, and tie", "cock, and bull", "coffee, and Danish", "cold, and starve", "come, and get it", "come, and go", "come, and gone", "come back, and see us", "coming, and going", "comings, and goings", "control, and status", "cook, and bottlewasher", "copy, and paste", "crash, and burn", "cry, and no wool", "cut, and dried", "cut, and run", "cut, and thrust", "dark, and handsome", "day, and age", "day, and night", "days, and holidays", "dead, and buried", "dead, and gone", "deaf, and dumb", "death, and taxes", "desert, and reward", "devil, and deep blue sea", "devil, and the deep blue sea", "dine, and dash", "divide, and conquer", "divide, and govern", "divide, and rule", "do's, and don'ts", "dog, and bone", "dog, and pony", "dog, and wolf", "dogs, and cats", "dollars, and cents", "done, and done", "done, and dusted", "doom, and gloom", "dos, and don'ts", "dot the I's, and cross the T's", "dot the i's, and cross the t's", "down, and die", "down, and dirty", "down, and out", "down, and outer", "draw, and quarter", "drawn, and quartered", "dribs, and drabs", "drink, and be merry", "drop, and a sudden", "drunk, and disorderly", "dry up, and blow away", "duck, and cover", "duck, and dive", "ducking, and diving", "ducks, and drakes", "dust, and ashes", "each, and every", "east, and west", "eat, and run", "ebb, and flow", "effing, and blinding", "elders, and betters", "enough, and some", "enough, and to spare", "errors, and omissions", "ever, and a day", "ever, and again", "everybody, and his", "everybody, and his brother", "everybody, and his cousin", "everybody, and their", "everyone, and their", "everything, and the", "eyes, and ears", "fair, and impartial", "fair, and square", "fair field, and no favour", "far, and away", "far, and near", "far, and wide", "fast, and furious", "fast, and loose", "faster, and faster", "fat, and happy", "fat, and sassy", "fear, and loathing", "fend, and prove", "fetch, and carry", "fever, and run", "few, and far between", "fights, and run", "fine, and dandy", "fingers, and thumbs", "fire, and brimstone", "fire, and water", "first, and foremost", "first, and last", "fit, and trim", "fits, and starts", "five, and dime", "five, and ten", "flesh, and blood", "flora, and fauna", "flotsam, and jetsam", "fool, and his money", "footloose, and fancy", "fore, and aft", "forever, and ever", "forgive, and forget", "form, and substance", "forward, and backward", "forwards, and backwards", "free, and clear", "free, and easy", "fresh, and sweet", "frog, and toad", "front, and center", "fun, and games", "fur, and feather", "fuss, and feathers", "gall, and wormwood", "give, and take", "gloom, and doom", "go, and chase", "go, and do", "gone, and done", "good, and all", "good, and proper", "good, and quickly", "good, and ready", "good news, and bad news", "goods, and chattels", "grab, and go", "great, and small", "great, and the good", "grin, and bear it", "hair, and hide", "hale, and hearty", "hammer, and sickle", "hammer, and tongs", "hand, and foot", "hand, and glove", "hands, and knees", "hands, and the cook", "hard, and fast", "haul off, and do", "hawk, and buzzard", "hawks, and doves", "head, and shoulders", "heart, and soul", "hearth, and home", "hearts, and flowers", "hearts, and minds", "heaven, and earth", "hell, and back", "hell, and gone", "hell, and half", "hell, and high", "hellfire, and damnation", "hem, and haw", "here, and now", "here, and there", "hide, and seek", "high, and dry", "high, and low", "high, and mighty", "highways, and byways", "hill, and down", "hire, and fire", "hit, and miss", "hit, and run", "hither, and tither", "hole, and corner", "home, and dry", "home, and hosted", "honest, and above", "hoops, and a holler", "hoot, and a half", "horns, and rattles", "horse, and buggy", "horse, and carriage", "horse, and rabbit", "hot, and bothered", "hot, and cold", "hot, and heavy", "house, and home", "howdy, and a half", "hue, and a cry", "hue, and cry", "huff, and puff", "hugs, and kisses", "hum, and haw", "hundred, and ten", "hurry up, and wait", "hustle, and bustle", "ifs, and buts", "in, and of itself", "in, and out", "in, and week", "information, and communication technology", "ins, and outs", "inside, and out", "intents, and purposes", "jigs, and the reels", "jot, and tittle", "juice, and cookies", "kicking, and screaming", "kicks, and for giggles", "kicks, and for laughs", "kiss, and cry", "kiss, and tell", "kit, and caboodle", "kith, and kin", "knife, and fork", "ladies, and gentlemen", "lares, and penates", "large, and in charge", "large as life, and twice as ugly", "lark, and on a lark", "laugh, and grow", "law, and order", "lean, and mean", "leaps, and bounds", "left, and right", "length, and breadth", "less, and less", "lick, and a promise", "life, and death", "life, and limb", "life, and soul", "line, and sinker", "little, and care", "live, and breathe", "live, and let", "live, and well", "lives, and breathes", "living, and breathing", "lo, and behold", "lo, and beyond", "loaves, and fishes", "lock, and key", "long, and hard", "long, and life", "long, and prosper", "long, and short", "long, and the short", "look, and feel", "lord, and master", "lost, and found", "lost, and gone", "loud, and clear", "love, and care", "love, and hate", "love, and war", "low, and sing", "make do, and mend", "man, and boy", "man, and wife", "many, and many", "me, and my", "me, and you", "meat, and drink", "meat, and no potatoes", "meet, and greet", "men, and true", "men, and women", "might, and main", "miles, and miles", "milk, and honey", "milk, and water", "million, and one", "mix, and match", "mix, and mingle", "mom, and apple", "money, and run", "moon, and back", "moon, and the milkman", "moon, and the stars", "moonlight, and roses", "mops, and brooms", "more, and more", "mouth, and trousers", "mover, and a shaker", "mover, and shaker", "movers, and shakers", "myself, and I", "name, and address", "name, and shame", "near, and dear", "near, and far", "nearest, and dearest", "neat, and tidy", "neck, and crop", "neck, and neck", "nerve, and muscle", "nice, and peaceful", "nickel, and dime", "night, and day", "nip, and tuck", "nod, and a wink", "nook, and cranny", "nooks, and crannies", "north, and south", "nothing, and care", "now, and again", "now, and anon", "now, and then", "nudge, and a wink", "null, and void", "nuts, and bolts", "oak, and iron", "odd, and curious", "odds, and ends", "odds, and sods", "off, and on", "off, and running", "oil, and water", "on, and about", "on, and off", "once, and again", "once, and for", "once, and for all", "once, and future", "one, and a", "one, and all", "one, and cheese", "one, and flesh", "one, and half", "one, and only", "one, and the same", "onward, and upward", "onwards, and upwards", "open, and above", "open, and shut", "out, and about", "out, and out", "over, and about", "over, and above", "over, and done", "over, and out", "over, and over", "pain, and suffering", "part, and parcel", "party, and play", "peace, and quiet", "peaches, and cream", "pen, and ink", "people, and true", "pick, and choose", "pick, and mix", "pinch, and a punch", "pinch, and scrape", "pink it, and shrink it", "pins, and needles", "pipe, and smoke", "piss, and moan", "piss, and vinegar", "piss, and wind", "pitch in, and help", "pitchforks, and hammer", "pith, and moment", "plain, and simple", "plug, and play", "pomp, and circumstance", "postage, and handling", "present, and correct", "pride, and joy", "prim, and proper", "pros, and cons", "prunes, and prisms", "pudding, and tame", "puff, and blow", "puff, and pant", "pure, and simple", "purely, and simply", "quick, and dirty", "quick, the dead", "r, and r", "rack, and ruin", "rain cats, and dogs", "rainbows, and unicorns", "rank, and file", "rant, and rave", "read it, and weep", "read.em, and weep", "ready, and willing", "real, and for true", "really, and truly", "rest, and relax", "right, and center", "right, and centre", "right, and left", "rinse, and repeat", "rise, and shine", "rises, and sets", "rock, and roll", "room, and board", "root, and branch", "rough, and ready", "rough, and tumble", "round, and round", "sackcloth, and ashes", "sadder, and wiser", "safe, and sound", "said, and done", "salt, and pepper", "score, and seven", "score, and ten", "scot, and lot", "scotch, and notch", "scratch, and find", "scrimp, and save", "sealed, and delivered", "search, and destroy", "shilling, and found", "shirts, and skins", "shock, and awe", "short, and curlies", "short, and sweet", "short, and the long", "shot, and powder", "show, and tell", "shreds, and patches", "shrink it, and pink it", "shut up, and take", "sick, and tired", "side, and down", "signed, and sealed", "sit back, and enjoy", "sit back, and let", "sit up, and take", "six, and two threes", "sizzle, and no steak", "skin, and bone", "slash, and burn", "sling, and arrows", "slings, and arrows", "slower, and slower", "slowly, and surely", "smoke, and mirrors", "snakes, and ladders", "so, and so", "softly, and carry", "song, and dance", "spic, and span", "spick, and span", "spit, and image", "spit, and polish", "spit, and sawdust", "stage, and off", "stand, and deliver", "stand up, and be", "stars, and stripes", "sticks, and stones", "still, and all", "stop, and smell", "straight, and narrow", "strikes, and you", "stuff, and nonsense", "such, and such", "suck it, and see", "sugar, and spice", "sum, and substance", "summer, and winter", "sunshine, and rainbows", "supply, and demand", "surf, and turf", "sweat, and tears", "sweet, and sour", "sweetness, and light", "swift, and sure", "swing, and a miss", "swings, and roundabouts", "sword, and sandal", "sword, and sorcery", "tag, and rag", "tail, and run", "talk, and no action", "talk, and no trousers", "tar, and feather", "tarred, and feathered", "tax, and spend", "tea, and sympathy", "team, and the dog", "them, and leave", "them, and us", "then, and there", "there, and back", "there, and then", "thick, and fast", "thick, and thin", "this, and that", "thoughts, and prayers", "thousand, and one", "thread, and thrum", "thrills, and spills", "through, and through", "thrust, and parry", "thus, and so", "thus, and such", "thus, and thus", "time, and a place", "time, and again", "time, and material", "time, and place", "time, and tide", "time, and time", "tired, and emotional", "tither, and yon", "to, and fro", "today, and gone", "toing, and froing", "tooth, and claw", "tooth, and nail", "top, and tail", "toss, and turn", "tossing, and turning", "touch, and go", "town, and gown", "track, and field", "tree, and leave", "trial, and error", "trials, and tribulations", "tried, and tested", "tried, and true", "tried, and trusted", "trouble, and strife", "turn, and turn", "tweedledee, and tweedledum", "tweedledum, and tweedledee", "two, and two", "um, and aah", "um, and ah", "underpromise, and overdeliver", "up, and about", "up, and around", "up, and at", "up, and away", "up, and comer", "up, and coming", "up, and did", "up, and die", "up, and doing", "up, and down", "up, and go", "up, and leave", "up, and nowhere", "up, and running", "up, and salted", "up, and up", "ups, and downs", "us, and them", "various, and sundry", "vim, and vigor", "vim, and vigour", "waifs, and strays", "wait, and see", "wake up, and smell", "walk, and chew", "walk, and talk", "warm, and fuzzy", "warp, and woof", "warts, and all", "wash, and wear", "wax, and wane", "way, and that", "ways, and means", "weal, and woe", "wear, and tear", "weighed, and found", "weird, and wonderful", "well, and good", "well, and truly", "wheel, and deal", "wheeling, and dealing", "whips, and jingles", "whistle, and flute", "whoop, and a holler", "whys, and wherefores", "wild, and woolly", "will, and testament", "willing, and able", "wind, and water", "wine, and dine", "wing, and a prayer", "wise, and dollar", "wise, and pound", "women, and children", "wool, and no shoddy", "work, and no play", "world, and his", "wormwood, and gall", "wrack, and ruin", "you and me"]
and_no_comma = ["A and B", "Adam and Eve", " and a half", " and a third", " and eighty", " and fifty", " and five", " and forty", " and ninety", " and ninety five", " and ninety nine", " and seventy", " and sixty", " and ten", " and thirty", " and three quarters", " and twenty", "B and B", "Bonnie and Clyde", "East and West", "Herb and Al", "Jekyll and Hyde", "Netflix and chill", "North and South", "Sam and Dave", "Siegfried and Roy", "Stars and Stripes", "Summer and Winter", "a boon and a bane", "a day late and a dollar short", "about and scatter", "above and beyond", "acres and a mule", "act and deed", "again and again", "aid and abet", "airs and graces", "alarms and excursions", "alarums and excursions", "alive and kicking", "all and end", "all and some", "all and sundry", "all day and every", "all gas and gaiters", "all hat and no cattle", "alpha and omega", "apples and oranges", "arm and a leg", "armed and dangerous", "around and around", "art and part of", "arts and crafts", "assholes and elbows", "at sixes and sevens", "back and edge", "back and fill", "back and forth", "back and sides", "backward and forward", "backwards and forwards", "bait and switch", "ball and chain", "ball and run", "balls and strikes", "bam and scram", "banana and split", "bark and no bite", "beck and call", "bed and board", "bed and breakfast", "bee and buzz", "been and done", "beer and skittles", "before and after", "bells and buckets", "bells and whistles", "belt and braces", "bib and tucker", "big and bold", "binge and purge", "birds and the bees", "bitch and moan", "bits and bobs", "bits and pieces", "bitter and twisted", "black and blue", "black and tan", "black and white", "blink and you", "block and tackle", "blood and guts", "blood and iron", "blood and thunder", "blue and white", "blues and twos", "bob and weave", "body and soul", "boots and all", "born and bred", "born and raised", "bottle and glass", "bound and determined", "bow and scrape", "boys and girls", "boys and their toys", "brains and brawn", "brawn and no brain", "bread and butter", "bread and water", "break down and cry", "breaking and entering", "brick and mortar", "bricks and mortar", "bright and breezy", "bright-eyed and bushy-tailed", "bruised and battered", "buckle and tongue", "bull and cow", "burning and no ship", "by and by", "by and large", "bye and good", "cake and eat", "cake and have it", "cakes and ale", "cap and bells", "carrot and stick", "carrot and the stick", "cash and carry", "cat and dog", "cat and mouse", "cats and dogs", "cause and effect", "chalk and cheese", "chapter and verse", "checks and balances", "chicken and egg", "children and drunken", "children and fools", "chili and beans", "chip and dip", "chop and charge", "cloak and dagger", "close and personal", "close down and shut down", "coach and horses", "coat and no knickers", "coat and tie", "cock and bull", "coffee and Danish", "cold and starve", "come and get it", "come and go", "come and gone", "come back and see us", "coming and going", "comings and goings", "control and status", "cook and bottlewasher", "copy and paste", "crash and burn", "cry and no wool", "cut and dried", "cut and run", "cut and thrust", "dark and handsome", "day and age", "day and night", "days and holidays", "dead and buried", "dead and gone", "deaf and dumb", "death and taxes", "desert and reward", "devil and deep blue sea", "devil and the deep blue sea", "dine and dash", "divide and conquer", "divide and govern", "divide and rule", "do's and don'ts", "dog and bone", "dog and pony", "dog and wolf", "dogs and cats", "dollars and cents", "done and done", "done and dusted", "doom and gloom", "dos and don'ts", "dot the I's and cross the T's", "dot the i's and cross the t's", "down and die", "down and dirty", "down and out", "down and outer", "draw and quarter", "drawn and quartered", "dribs and drabs", "drink and be merry", "drop and a sudden", "drunk and disorderly", "dry up and blow away", "duck and cover", "duck and dive", "ducking and diving", "ducks and drakes", "dust and ashes", "each and every", "east and west", "eat and run", "ebb and flow", "effing and blinding", "elders and betters", "enough and some", "enough and to spare", "errors and omissions", "ever and a day", "ever and again", "everybody and his", "everybody and his brother", "everybody and his cousin", "everybody and their", "everyone and their", "everything and the", "eyes and ears", "fair and impartial", "fair and square", "fair field and no favour", "far and away", "far and near", "far and wide", "fast and furious", "fast and loose", "faster and faster", "fat and happy", "fat and sassy", "fear and loathing", "fend and prove", "fetch and carry", "fever and run", "few and far between", "fights and run", "fine and dandy", "fingers and thumbs", "fire and brimstone", "fire and water", "first and foremost", "first and last", "fit and trim", "fits and starts", "five and dime", "five and ten", "flesh and blood", "flora and fauna", "flotsam and jetsam", "fool and his money", "footloose and fancy", "fore and aft", "forever and ever", "forgive and forget", "form and substance", "forward and backward", "forwards and backwards", "free and clear", "free and easy", "fresh and sweet", "frog and toad", "front and center", "fun and games", "fur and feather", "fuss and feathers", "gall and wormwood", "give and take", "gloom and doom", "go and chase", "go and do", "gone and done", "good and all", "good and proper", "good and quickly", "good and ready", "good news and bad news", "goods and chattels", "grab and go", "great and small", "great and the good", "grin and bear it", "hair and hide", "hale and hearty", "hammer and sickle", "hammer and tongs", "hand and foot", "hand and glove", "hands and knees", "hands and the cook", "hard and fast", "haul off and do", "hawk and buzzard", "hawks and doves", "head and shoulders", "heart and soul", "hearth and home", "hearts and flowers", "hearts and minds", "heaven and earth", "hell and back", "hell and gone", "hell and half", "hell and high", "hellfire and damnation", "hem and haw", "here and now", "here and there", "hide and seek", "high and dry", "high and low", "high and mighty", "highways and byways", "hill and down", "hire and fire", "hit and miss", "hit and run", "hither and tither", "hole and corner", "home and dry", "home and hosted", "honest and above", "hoops and a holler", "hoot and a half", "horns and rattles", "horse and buggy", "horse and carriage", "horse and rabbit", "hot and bothered", "hot and cold", "hot and heavy", "house and home", "howdy and a half", "hue and a cry", "hue and cry", "huff and puff", "hugs and kisses", "hum and haw", "hundred and ten", "hurry up and wait", "hustle and bustle", "ifs and buts", "in and of itself", "in and out", "in and week", "information and communication technology", "ins and outs", "inside and out", "intents and purposes", "jigs and the reels", "jot and tittle", "juice and cookies", "kicking and screaming", "kicks and for giggles", "kicks and for laughs", "kiss and cry", "kiss and tell", "kit and caboodle", "kith and kin", "knife and fork", "ladies and gentlemen", "lares and penates", "large and in charge", "large as life and twice as ugly", "lark and on a lark", "laugh and grow", "law and order", "lean and mean", "leaps and bounds", "left and right", "length and breadth", "less and less", "lick and a promise", "life and death", "life and limb", "life and soul", "line and sinker", "little and care", "live and breathe", "live and let", "live and well", "lives and breathes", "living and breathing", "lo and behold", "lo and beyond", "loaves and fishes", "lock and key", "long and hard", "long and life", "long and prosper", "long and short", "long and the short", "look and feel", "lord and master", "lost and found", "lost and gone", "loud and clear", "love and care", "love and hate", "love and war", "low and sing", "make do and mend", "man and boy", "man and wife", "many and many", "me and my", "me and you", "meat and drink", "meat and no potatoes", "meet and greet", "men and true", "men and women", "might and main", "miles and miles", "milk and honey", "milk and water", "million and one", "mix and match", "mix and mingle", "mom and apple", "money and run", "moon and back", "moon and the milkman", "moon and the stars", "moonlight and roses", "mops and brooms", "more and more", "mouth and trousers", "mover and a shaker", "mover and shaker", "movers and shakers", "myself and I", "name and address", "name and shame", "near and dear", "near and far", "nearest and dearest", "neat and tidy", "neck and crop", "neck and neck", "nerve and muscle", "nice and peaceful", "nickel and dime", "night and day", "nip and tuck", "nod and a wink", "nook and cranny", "nooks and crannies", "north and south", "nothing and care", "now and again", "now and anon", "now and then", "nudge and a wink", "null and void", "nuts and bolts", "oak and iron", "odd and curious", "odds and ends", "odds and sods", "off and on", "off and running", "oil and water", "on and about", "on and off", "once and again", "once and for", "once and for all", "once and future", "one and a", "one and all", "one and cheese", "one and flesh", "one and half", "one and only", "one and the same", "onward and upward", "onwards and upwards", "open and above", "open and shut", "out and about", "out and out", "over and about", "over and above", "over and done", "over and out", "over and over", "pain and suffering", "part and parcel", "party and play", "peace and quiet", "peaches and cream", "pen and ink", "people and true", "pick and choose", "pick and mix", "pinch and a punch", "pinch and scrape", "pink it and shrink it", "pins and needles", "pipe and smoke", "piss and moan", "piss and vinegar", "piss and wind", "pitch in and help", "pitchforks and hammer", "pith and moment", "plain and simple", "plug and play", "pomp and circumstance", "postage and handling", "present and correct", "pride and joy", "prim and proper", "pros and cons", "prunes and prisms", "pudding and tame", "puff and blow", "puff and pant", "pure and simple", "purely and simply", "quick and dirty", "quick and the dead", "r and r", "rack and ruin", "rain cats and dogs", "rainbows and unicorns", "rank and file", "rant and rave", "read it and weep", "read.em and weep", "ready and willing", "real and for true", "really and truly", "rest and relax", "right and center", "right and centre", "right and left", "rinse and repeat", "rise and shine", "rises and sets", "rock and roll", "room and board", "root and branch", "rough and ready", "rough and tumble", "round and round", "sackcloth and ashes", "sadder and wiser", "safe and sound", "said and done", "salt and pepper", "score and seven", "score and ten", "scot and lot", "scotch and notch", "scratch and find", "scrimp and save", "sealed and delivered", "search and destroy", "shilling and found", "shirts and skins", "shock and awe", "short and curlies", "short and sweet", "short and the long", "shot and powder", "show and tell", "shreds and patches", "shrink it and pink it", "shut up and take", "sick and tired", "side and down", "signed and sealed", "sit back and enjoy", "sit back and let", "sit up and take", "six and two threes", "sizzle and no steak", "skin and bone", "slash and burn", "sling and arrows", "slings and arrows", "slower and slower", "slowly and surely", "smoke and mirrors", "snakes and ladders", "so and so", "softly and carry", "song and dance", "spic and span", "spick and span", "spit and image", "spit and polish", "spit and sawdust", "stage and off", "stand and deliver", "stand up and be", "stars and stripes", "sticks and stones", "still and all", "stop and smell", "straight and narrow", "strikes and you", "stuff and nonsense", "such and such", "suck it and see", "sugar and spice", "sum and substance", "summer and winter", "sunshine and rainbows", "supply and demand", "surf and turf", "sweat and tears", "sweet and sour", "sweetness and light", "swift and sure", "swing and a miss", "swings and roundabouts", "sword and sandal", "sword and sorcery", "tag and rag", "tail and run", "talk and no action", "talk and no trousers", "tar and feather", "tarred and feathered", "tax and spend", "tea and sympathy", "team and the dog", "them and leave", "them and us", "then and there", "there and back", "there and then", "thick and fast", "thick and thin", "this and that", "thoughts and prayers", "thousand and one", "thread and thrum", "thrills and spills", "through and through", "thrust and parry", "thus and so", "thus and such", "thus and thus", "time and a place", "time and again", "time and material", "time and place", "time and tide", "time and time", "tired and emotional", "tither and yon", "to and fro", "today and gone", "toing and froing", "tooth and claw", "tooth and nail", "top and tail", "toss and turn", "tossing and turning", "touch and go", "town and gown", "track and field", "tree and leave", "trial and error", "trials and tribulations", "tried and tested", "tried and true", "tried and trusted", "trouble and strife", "turn and turn", "tweedledee and tweedledum", "tweedledum and tweedledee", "two and two", "um and aah", "um and ah", "underpromise and overdeliver", "up and about", "up and around", "up and at", "up and away", "up and comer", "up and coming", "up and did", "up and die", "up and doing", "up and down", "up and go", "up and leave", "up and nowhere", "up and running", "up and salted", "up and up", "ups and downs", "us and them", "various and sundry", "vim and vigor", "vim and vigour", "waifs and strays", "wait and see", "wake up and smell", "walk and chew", "walk and talk", "warm and fuzzy", "warp and woof", "warts and all", "wash and wear", "wax and wane", "way and that", "ways and means", "weal and woe", "wear and tear", "weighed and found", "weird and wonderful", "well and good", "well and truly", "wheel and deal", "wheeling and dealing", "whips and jingles", "whistle and flute", "whoop and a holler", "whys and wherefores", "wild and woolly", "will and testament", "willing and able", "wind and water", "wine and dine", "wing and a prayer", "wise and dollar", "wise and pound", "women and children", "wool and no shoddy", "work and no play", "world and his", "wormwood and gall", "wrack and ruin", "you and me"]

which_comma_inside = ["[^\w]against, which", "[^\w]and, which", "[^\w]any, which", "[^\w]at, which", "[^\w]by, which", "[^\w]ever, which", "[^\w]every, which", "[^\w]for, which", "[^\w]from, which", "[^\w]in, which", "[^\w]into, which", "[^\w]knew, which", "[^\w]know, which", "[^\w]know, which is which", "[^\w]manner, which", "[^\w]matter, which", "[^\w]near, which", "[^\w]of, which", "[^\w]on, which", "[^\w]one, which", "[^\w]see, which", "[^\w]something, which", "[^\w]tell, which is which", "[^\w]that, which", "[^\w]through, which", "[^\w]to, which", "[^\w]towards, which", "[^\w]upon, which", "[^\w]way, which", "[^\w]which, is which", "[^\w]with, which", "[^\w]above, which", "[^\w]after, which", "[^\w]before, which", "[^\w]behind, which", "[^\w]below, which", "[^\w]besides, which", "[^\w]during, which", "[^\w]in front of, which", "[^\w]over, which", "[^\w]those, which", "[^\w]under, which"]
which_no_comma = [", against which", ", and which", " any which", ", at which", ", by which", " ever which", " every which", ", for which", ", from which", ", in which", ", into which", " knew which", " know which", " know which is which", " manner which", " matter which", ", near which", ", of which", ", on which", " one which", " see which", " something which", " tell which is which", ", that which", ", through which", ", to which", ", towards which", ", upon which", " way which", " which is which", ", with which", ", above which", ", after which", ", before which", ", behind which", ", below which", ", besides which", ", during which", ", in front of which", ", over which", ", those which", ", under which"]

that_comma_inside = ["[^\w]'bout, that", "[^\w]about, that", "[^\w]above, that", "[^\w]after, that", "[^\w]all, that", "[^\w]along, that", "[^\w]and, that", "[^\w]around, that", "[^\w]as, that", "[^\w]at, that", "[^\w]be, that", "[^\w]because, that", "[^\w]before, that", "[^\w]behind, that", "[^\w]besides, that", "[^\w]beyond, that", "[^\w]but, that", "[^\w]by, that", "[^\w]did, that", "[^\w]do, that", "[^\w]does, that", "[^\w]done, that", "[^\w]during, that", "[^\w]even, that", "[^\w]except, that", "[^\w]fancy, that", "[^\w]for, that", "[^\w]from, that", "[^\w]fuck, that", "[^\w]he, that", "[^\w]how, that", "[^\w]if, that", "[^\w]in, that", "[^\w]is, that", "[^\w]isn[.]t, that", "[^\w]just, that", "[^\w]knew, that", "[^\w]know, that", "[^\w]leave, that", "[^\w]left, that", "[^\w]let, that", "[^\w]may, that", "[^\w]me, that", "[^\w]might, that", "[^\w]much, that", "[^\w] near, that", "[^\w]not, that", "[^\w]now, that", "[^\w]of, that", "[^\w]on, that", "[^\w]one, that", "[^\w]only, that", "[^\w]or, that", "[^\w]over, that", "[^\w]said, that", "[^\w]save, that", "[^\w]say, that", "[^\w]says, that", "[^\w]she, that", "[^\w], that", "[^\w]so, that", "[^\w]than, that", "[^\w]that settles, that", "[^\w]that's, that", "[^\w]then, that", "[^\w]they, that", "[^\w]those, that", "[^\w]to, that", "[^\w]under, that", "[^\w], that", "[^\w]upon, that", "[^\w]was, that", "[^\w]what, that", "[^\w]when, that", "[^\w]where, that", "[^\w]while, that", "[^\w]why, that", "[^\w]with, that", "[^\w]write, that", "[^\w]writes, that", "[^\w]wrote, that", "[^\w]believe, that", "[^\w]believing, that", "[^\w]came, that", "[^\w]case, that", "[^\w]come, that", "[^\w]didn[.]t, that", "[^\w]get, that", "[^\w]given, that", "[^\w]go, that", "[^\w]got, that", "[^\w]head, that", "[^\w]headed, that", "[^\w]heading, that", "[^\w]hear, that", "[^\w]heard, that", "[^\w]hearing, that", "[^\w]here[.]s, that", "[^\w]imagine, that", "[^\w]imagined, that", "[^\w]it[.]s, that", "[^\w]knowing, that", "[^\w]lie, that", "[^\w]lied, that", "[^\w]lies, that", "[^\w]like, that", "[^\w]make, that", "[^\w]mean, that", "[^\w]meant, that", "[^\w]mind, that", "[^\w]provided, that", "[^\w]roger, that", "[^\w]run, that", "[^\w]saw, that", "[^\w]scratch, that", "[^\w]see, that", "[^\w]seeing, that", "[^\w]take, that", "[^\w]tell, that", "[^\w]there[.]s, that", "[^\w]think, that", "[^\w]thought, that", "[^\w]told, that", "[^\w]unlike, that", "[^\w]wasn[.]t, that", "[^\w]went, that", "[^\w]what[.]s, that", "[^\w]will, that", "[^\w]would, that"]
that_no_comma = [" 'bout that", " about that", " above that", " after that", " all that", " along that", ", and that", " around that", " as that", " at that", " be that", " because that", " before that", " behind that", " besides that", " beyond that", " but that", " by that", " did that", " do that", " does that", " done that", " during that", " even that", " except that", " fancy that", " for that", " from that", " fuck that", " he that", " how that", " if that", " in that", " is that", " isn[.]t that", " just that", " knew that", " know that", " leave that", " left that", " let that", " may that", " me that", " might that", " much that", " near that", " not that", " now that", " of that", " on that", " one that", " only that", " or that", " over that", " said that", " save that", " say that", " says that", " she that", ", since that", " so that", " than that", " that settles that", " that's that", ", then that", " they that", " those that", " to that", " under that", ", until that", " upon that", " was that", " what that", " when that", " where that", " while that", " why that", " with that", " write that", " writes that", " wrote that", " believe that", " believing that", " came that", " case that", " come that", " didn[.]t that", " get that", " given that", " go that", " got that", " head that", " headed that", " heading that", " hear that", " heard that", " hearing that", " here[.]s that", " imagine that", " imagined that", " it[.]s that", " knowing that", " lie that", " lied that", " lies that", " like that", " make that", " mean that", " meant that", " mind that", " provided that", " roger that", " run that", " saw that", " scratch that", " see that", " seeing that", " take that", " tell that", " there[.]s that", " think that", " thought that", " told that", " unlike that", " wasn[.]t that", " went that", " what[.]s that", " will that", " would that"]

with open('/opt/lampp/htdocs/SpeakTheBeats/SpeakTheScript/EnglishDictionary.txt', 'r') as dictionary:
    dictionary_words = set(word.strip().lower() for word in dictionary)

text_chunks = [[]]
index = 0

whole_text = whole_text.replace('\ufeff', '').replace('_', '"').replace('<i>', '"').replace('</i>', '"')
initial_phoneme_tag_count = whole_text.count("<phoneme alphabet=")

#Replaces onomatopoeias with words that are more easily amenable to TTS (ex: '[^\w]Sh[h]+[^\w]' => 'Shush').
#I used [^\w] on either side of the patterns to exclude words such as 'Shirt'
#Including match[0] and match[-1] avoids losing the the characters on either side of the onomatopoeias following substitution.
#match_counts allows to convert every identical word matching a re pattern, and there can be several
#hits for a single re pattern (ex: Sh!, shh! for '[^\w]Sh[h]+[^\w]')
for pattern in onomatopoeias:
    pattern_matches = re.findall(pattern, whole_text)
    if pattern_matches != []:
        pattern_list_index = onomatopoeias.index(pattern)
        for match in pattern_matches:
            match_count = whole_text.count(match)
            for _ in range(match_count):
                whole_text = whole_text.replace(match, match[0] + modified_onomatopoeias[pattern_list_index] + match[-1], match_count)
for pattern in onomatopoeias:
    pattern_matches = re.findall(pattern.lower(), whole_text)
    if pattern_matches != []:
        pattern_list_index = onomatopoeias.index(pattern)
        for match in pattern_matches:
            match_count = whole_text.count(match)
            for _ in range(match_count):
                whole_text = whole_text.replace(match, match[0] + modified_onomatopoeias[pattern_list_index].lower() + match[-1], match_count)

for hyphen in hyphens:
    pattern = re.compile(hyphen)
    whole_text = re.sub(pattern, ', ', whole_text)

terminating_punctuation = "[!?.]"
sentences = [sentence.strip() for sentence in re.split(terminating_punctuation, whole_text)]
potentially_mispronounced_words = set()
set_sentences_many_commas = set()
commas_semicolons_per_word_for_every_sentence = []
sentences_word_counts = []

sentence_start_index = 0
for i in range(len(sentences)):
    #Making a list of all words in sentence (not space characters).
    sentence_words = re.split('\s|"|\'|:|;|,|\n|“|”', sentences[i])
    sentence_words = [w for w in sentence_words if w != '']
    sentences_word_counts.append(len(sentence_words))
    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')

    if len(sentence_words) > 0:
        commas_semicolons_per_word_for_every_sentence.append(comma_semicolon_count/sentences_word_counts[i])

commas_semicolons_whole_text_before_modifications = whole_text.count(',') + whole_text.count(';')

if sum(commas_semicolons_per_word_for_every_sentence) and len(commas_semicolons_per_word_for_every_sentence) and len(sentences) > 0:
    average_commas_semicolons_per_word_for_whole_text = sum(commas_semicolons_per_word_for_every_sentence)/len(commas_semicolons_per_word_for_every_sentence)
    standard_deviation = stdev(commas_semicolons_per_word_for_every_sentence)
    comma_semicolons_threshold = average_commas_semicolons_per_word_for_whole_text + standard_deviation
else:
    comma_semicolons_threshold = 0.2

#Here I define a cap for the threshold (average comma+semicolon/word count + standard deviation), because it wouldn't be desirable to add so many commas to a text already having a lot of commas.
if comma_semicolons_threshold > 0.2:
    comma_semicolons_threshold = 0.2

terminating_punctuation = "[!?.]"
sentences = [sentence.strip() for sentence in re.split(terminating_punctuation, whole_text)]
for i in range(len(sentences)):

    #Making a list of all words in sentence this is the second split, where the separators are included in the list of results (through the inclusion of
    #the regex expressions in parentheses). This is an important distinction, because the amended sentences[i] will be reconstituted with a join, after
    #substitution of a word containing digits and letters for a version of the word having a spacer (ex: L500 => L 500)
    sentence_words_second_split = re.split('(\s|"|\'|:|;|,|\n|“|”|‘|’|-)', sentences[i])
    sentence_words_second_split = [w for w in sentence_words_second_split if w != '']
    for word in sentence_words_second_split:

        #In the event that a number is directly preceded or followed by a non-digit character other than a comma or a period, it wouldn't be
        #read properly by TTS. The code below allows to add a space between these characters and the digits.
        if (re.search('[\d]', word) != None and re.search('[^\d^.^,]', word) != None):
            #Need to preserve 1st, 2nd, 3rd, 4th and so on for it to read well, all other units can be read at a space interval from the digit.
            #Finds all digits in word separated by letters or beginning or end of word. If there is only one digit, the code will split the
            #words from the digit, so that it may be more easily readable by TTS.
            if 'st' not in word and 'nd' not in word and 'rd' not in word and 'th' not in word:
                word_digits = re.findall('\d+', word)
                digits_index_start = word.index(word_digits[0])
                digits_length = len(word_digits[0])
                if len(word_digits) > 1:
                    pass
                else:
                    if ((digits_index_start > 0) and (digits_index_start + digits_length < len(word))):
                        new_word_with_space = word[:digits_index_start] + ' ' + word[digits_index_start:(digits_index_start+digits_length)] + ' ' + word[(digits_index_start+digits_length):]
                    else:
                        if digits_index_start == 0:
                            new_word_with_space = word[digits_index_start:(digits_index_start+digits_length)] + ' ' + word[(digits_index_start+digits_length):]
                        elif digits_index_start > 0:
                            new_word_with_space = word[:digits_index_start] + ' ' + word[digits_index_start:]
                    sentence_words_second_split[sentence_words_second_split.index(word)] = new_word_with_space

    old_sentence = sentences[i]
    sentences[i] = ''.join(sentence_words_second_split)
    whole_text = whole_text.replace(old_sentence, sentences[i])

    for word in sentence_words_second_split:
        #Building a set of potentially mispronounced capitalized words and words having 3 or more of the same letter in succession, or words not exclusively comprised of letters or numbers.
        if (word[0].isupper() and word.isalpha() and word.lower() not in dictionary_words and ' ' + word not in modified_onomatopoeias):
            potentially_mispronounced_words.add(word)
        for char_index in range(len(word)-2):
            if ((word.isalpha() and (word[char_index] == word[char_index+1] and word[char_index+1] == word[char_index+2])) or (word.isnumeric() == False and word.isalpha() == False and word[-2:] not in ['st', 'nd', 'rd', 'th'] and word != "********************")):
                potentially_mispronounced_words.add(word)

    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')
    #Only perform the substitutions below in the sentences that have a comma/word count ratio below comma_semicolons_threshold, which can be up to 0.2.
    if (sentences_word_counts[i] > 0 and comma_semicolon_count/sentences_word_counts[i] < comma_semicolons_threshold):

        for phrase_index in range(len(linking_words_middle_of_sentence_no_comma)):
            pattern = re.compile(linking_words_middle_of_sentence_no_comma[phrase_index])
            if pattern.search(sentences[i]) != None:
                old_sentence = sentences[i]
                sentences[i] = re.sub(pattern, linking_words_middle_of_sentence_with_comma[phrase_index], sentences[i])
                whole_text = whole_text.replace(old_sentence, sentences[i])
        if (sentences_word_counts[i] > 10 and (comma_semicolon_count/sentences_word_counts[i] > comma_semicolons_threshold)):
            set_sentences_many_commas.add(i)
#Since these substitutions are for phrases containing several words, they can be done throughout the "whole_text",
#at the end of a 'for i in range(len(sentences))' loop.
for phrase_index in range(len(but_middle_of_sentence_comma_inside)):
    pattern = re.compile(but_middle_of_sentence_comma_inside[phrase_index])
    whole_text = re.sub(pattern, but_middle_of_sentence_no_comma[phrase_index], whole_text)

terminating_punctuation = "[!?.]"
sentences = [sentence.strip() for sentence in re.split(terminating_punctuation, whole_text)]
for i in range(len(sentences)):
    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')
    #Only perform the substitutions below in the sentences that have a comma/word count ratio below comma_semicolons_threshold, which can be up to 0.2.
    if (sentences_word_counts[i] > 0 and comma_semicolon_count/sentences_word_counts[i] < comma_semicolons_threshold):
        #Making a list of all words in sentence this is the second split, where the separators are included in the list of results (through the inclusion of
        #the regex expressions in parentheses). This is an important distinction, because the amended sentences[i] will be reconstituted with a join, after
        #substitution of a word containing digits and letters for a version of the word having a spacer (ex: L500 => L 500)
        sentence_words_second_split = re.split('(\s|"|\'|:|;|,|\n|“|”|‘|’|-)', sentences[i])
        sentence_words_second_split = [w for w in sentence_words_second_split if w != '']
        #When looking up if the sentence_first_word is in linking_words_start_of_sentence_no_comma, a space is added after sentence_first_word, because
        #the linking words in the list have a space after them. Due to the presence of Byte Order Marks ('\ufeff'), a string replace method is added to remove BOMs.
        #The index of the first colon or comma in the sentence will be compared to those of instances of linking_words_start_of_sentence_no_comma' at the start of the sentence.
        #Commas will be added after the linking_word if there is more than 20 characters between the first comma or semicolon and the index after the linking_word.
        sentence_first_word = sentence_words_second_split[0]
        if sentence_first_word in linking_words_start_of_sentence_no_comma:
            index_first_comma_semicolon = re.search(',|;', sentences[i]).start()
            phrase_index = linking_words_start_of_sentence_no_comma.index(sentence_first_word + ' ')
            linking_word_threshold = len(sentence_first_word) + 20
            if linking_word_threshold < index_first_comma_semicolon:
                old_sentence = sentences[i]
                sentences[i] = re.sub(sentence_first_word, linking_words_start_of_sentence_with_comma[phrase_index], sentences[i])
                whole_text = whole_text.replace(old_sentence, sentences[i])

        #The indices of the colons and commas will be compared to those of instances of 'yet'. Should instances of 'yet'
        #be within 20 characters (about 3.5 words+spaces) of a comma or a semicolon, no substitution will take place to introduce further commas.
        commas_semicolons_matches = re.finditer(',|;', sentences[i])
        commas_semicolons_indices_list = [m.start() for m in commas_semicolons_matches]
        #This can get confusing, as I refer to element indexes of lists of indexes. Read the variable titles carefully. Also, I include [\s]? (1 whitespace character,
        #including carriage returns, on either side of the 'yet' keyword) to include matches for 'yet' which might occur at the very beginning (without a space to the left)
        #or the very end of a line (without a space to the right).
        yet_matches = re.finditer('[\s]yet[\s]', sentences[i])
        yet_indices_list = [m.start() for m in yet_matches]
        for yet_index in yet_indices_list:
            index_difference_list = []
            for punct_index in commas_semicolons_indices_list:
                index_difference_list.append(abs(yet_index-punct_index))
            if (all(difference >= 20 for difference in index_difference_list) and (len(sentences[i]) - yet_index > 20)):
                #print('\n\nThe "yet" at index ' + str(yet_index) + ' was over about 3.5 words+spaces of either a comma or a semicolon in sentence and will get a comma.\n\n')
                if yet_indices_list.index(yet_index) < len(yet_indices_list)-1:
                    next_yet_index = yet_indices_list[yet_indices_list.index(yet_index)+1]
                    new_sentence = re.sub('[\s]yet', ', yet', sentences[i][yet_index: next_yet_index])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:yet_index] + new_sentence + sentences[i][next_yet_index:]
                    whole_text = whole_text.replace(old_sentence, sentences[i])
                else:
                    new_sentence = re.sub('[\s]yet', ', yet', sentences[i][yet_index:])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:yet_index] + new_sentence
                    whole_text = whole_text.replace(old_sentence, sentences[i])
        if (sentences_word_counts[i] > 10 and (comma_semicolon_count/sentences_word_counts[i] > comma_semicolons_threshold)):
            set_sentences_many_commas.add(i)
#Since these substitutions are for phrases containing several words, they can be done throughout the "whole_text",
#at the end of a 'for i in range(len(sentences))' loop.
for phrase_index in range(len(yet_comma_inside_capitalized)):
    pattern = re.compile(yet_comma_inside_capitalized[phrase_index])
    whole_text = re.sub(pattern, yet_no_comma_capitalized[phrase_index], whole_text)
for phrase_index in range(len(yet_comma_inside_lowercase)):
    pattern = re.compile(yet_comma_inside_lowercase[phrase_index])
    whole_text = re.sub(pattern, yet_no_comma_lowercase[phrase_index], whole_text)

terminating_punctuation = "[!?.]"
sentences = [sentence.strip() for sentence in re.split(terminating_punctuation, whole_text)]
for i in range(len(sentences)):
    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')
    #Only perform the substitutions below in the sentences that have a comma/word count ratio below comma_semicolons_threshold, which can be up to 0.2.
    if (sentences_word_counts[i] > 0 and comma_semicolon_count/sentences_word_counts[i] < comma_semicolons_threshold):

        #The indices of the colons and commas will be compared to those of instances of 'or'. Should instances of 'or'
        #be within 20 characters (about 3.5 words+spaces) of a comma or a semicolon, no substitution will take place to introduce further commas.
        commas_semicolons_matches = re.finditer(',|;', sentences[i])
        commas_semicolons_indices_list = [m.start() for m in commas_semicolons_matches]
        #This can get confusing, as I refer to element indexes of lists of indexes. Read the variable titles carefully.
        or_matches = re.finditer('[\s]or[\s]', sentences[i])
        or_indices_list = [m.start() for m in or_matches]
        for or_index in or_indices_list:
            index_difference_list = []
            for punct_index in commas_semicolons_indices_list:
                index_difference_list.append(abs(or_index-punct_index))
            if (all(difference >= 20 for difference in index_difference_list) and (len(sentences[i]) - or_index > 20)):
                #print('\n\nThe "or" at index ' + str(or_index) + ' was over about 3.5 words+spaces of either a comma or a semicolon in sentence and will get a comma.\n\n')
                if or_indices_list.index(or_index) < len(or_indices_list)-1:
                    next_or_index = or_indices_list[or_indices_list.index(or_index)+1]
                    new_sentence = re.sub('[\s]or', ', or', sentences[i][or_index: next_or_index])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:or_index] + new_sentence + sentences[i][next_or_index:]
                    whole_text = whole_text.replace(old_sentence, sentences[i])
                else:
                    new_sentence = re.sub('[\s]or', ', or', sentences[i][or_index:])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:or_index] + new_sentence
                    whole_text = whole_text.replace(old_sentence, sentences[i])
        if (sentences_word_counts[i] > 10 and (comma_semicolon_count/sentences_word_counts[i] > comma_semicolons_threshold)):
            set_sentences_many_commas.add(i)
#Since these substitutions are for phrases containing several words, they can be done throughout the "whole_text",
#at the end of a 'for i in range(len(sentences))' loop.
for phrase_index in range(len(or_comma_inside)):
    pattern = re.compile(or_comma_inside[phrase_index])
    whole_text = re.sub(pattern, or_no_comma[phrase_index], whole_text)
for phrase_index in range(len(or_comma_inside)):
    pattern = re.compile(or_comma_inside[phrase_index].lower())
    whole_text = re.sub(pattern, or_no_comma[phrase_index].lower(), whole_text)

terminating_punctuation = "[!?.]"
sentences = [sentence.strip() for sentence in re.split(terminating_punctuation, whole_text)]
for i in range(len(sentences)):
    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')
    #Only perform the substitutions below in the sentences that have a comma/word count ratio below comma_semicolons_threshold, which can be up to 0.2.
    if (sentences_word_counts[i] > 0 and comma_semicolon_count/sentences_word_counts[i] < comma_semicolons_threshold):

        #The indices of the colons and commas will be compared to those of instances of 'and'. Should instances of 'and'
        #be within 20 characters (about 3.5 words+spaces) of a comma or a semicolon, no substitution will take place to introduce further commas.
        commas_semicolons_matches = re.finditer(',|;', sentences[i])
        commas_semicolons_indices_list = [m.start() for m in commas_semicolons_matches]
        #This can get confusing, as I refer to element indexes of lists of indexes. Read the variable titles carefully.
        and_matches = re.finditer('[\s]and[\s]', sentences[i])
        and_indices_list = [m.start() for m in and_matches]
        for and_index in and_indices_list:
            index_difference_list = []
            for punct_index in commas_semicolons_indices_list:
                index_difference_list.append(abs(and_index-punct_index))
            if (all(difference >= 20 for difference in index_difference_list) and (len(sentences[i]) - and_index > 20) and (and_index > 20)):
                #print('\n\nThe "and" at index ' + str(and_index) + ' was over 20 characters (about 3.5 words+spaces) of either a comma or a semicolon in sentence and will get a comma.\n\n')
                if and_indices_list.index(and_index) < len(and_indices_list)-1:
                    next_and_index = and_indices_list[and_indices_list.index(and_index)+1]
                    new_sentence = re.sub('[\s]and', ', and', sentences[i][and_index: next_and_index])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:and_index] + new_sentence + sentences[i][next_and_index:]
                    whole_text = whole_text.replace(old_sentence, sentences[i])
                else:
                    new_sentence = re.sub('[\s]and', ', and', sentences[i][and_index:])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:and_index] + new_sentence
                    whole_text = whole_text.replace(old_sentence, sentences[i])
        if (sentences_word_counts[i] > 10 and (comma_semicolon_count/sentences_word_counts[i] > comma_semicolons_threshold)):
            set_sentences_many_commas.add(i)
#Since these substitutions are for phrases containing several words, they can be done throughout the "whole_text",
#at the end of a 'for i in range(len(sentences))' loop.
for phrase_index in range(len(and_comma_inside)):
    pattern = re.compile(and_comma_inside[phrase_index])
    whole_text = re.sub(pattern, and_no_comma[phrase_index], whole_text)

terminating_punctuation = "[!?.]"
sentences = [sentence.strip() for sentence in re.split(terminating_punctuation, whole_text)]
for i in range(len(sentences)):
    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')
    #Only perform the substitutions below in the sentences that have a comma/word count ratio below comma_semicolons_threshold, which can be up to 0.2.
    if (sentences_word_counts[i] > 0 and comma_semicolon_count/sentences_word_counts[i] < comma_semicolons_threshold):

        #The indices of the colons and commas will be compared to those of instances of 'which'. Should instances of 'which'
        #be within 20 characters (about 3.5 words+spaces) of a comma or a semicolon, no substitution will take place to introduce further commas.
        commas_semicolons_matches = re.finditer(',|;', sentences[i])
        commas_semicolons_indices_list = [m.start() for m in commas_semicolons_matches]
        #This can get confusing, as I refer to element indexes of lists of indexes. Read the variable titles carefully.
        which_matches = re.finditer('[\s]which[\s]', sentences[i])
        which_indices_list = [m.start() for m in which_matches]
        for which_index in which_indices_list:
            index_difference_list = []
            for punct_index in commas_semicolons_indices_list:
                index_difference_list.append(abs(which_index-punct_index))
            if (all(difference >= 20 for difference in index_difference_list) and (len(sentences[i]) - which_index > 20) and (which_index > 20)):
                #print('\n\nThe "which" at index ' + str(which_index) + ' was over about 3.5 words+spaces of either a comma or a semicolon in sentence and will get a comma.\n\n')
                if which_indices_list.index(which_index) < len(which_indices_list)-1:
                    next_which_index = which_indices_list[which_indices_list.index(which_index)+1]
                    new_sentence = re.sub('[\s]which', ', which', sentences[i][which_index: next_which_index])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:which_index] + new_sentence + sentences[i][next_which_index:]
                    whole_text = whole_text.replace(old_sentence, sentences[i])
                else:
                    new_sentence = re.sub('[\s]which', ', which', sentences[i][which_index:])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:which_index] + new_sentence
                    whole_text = whole_text.replace(old_sentence, sentences[i])

        if (sentences_word_counts[i] > 10 and (comma_semicolon_count/sentences_word_counts[i] > comma_semicolons_threshold)):
            set_sentences_many_commas.add(i)
#Since these substitutions are for phrases containing several words, they can be done throughout the "whole_text",
#at the end of a 'for i in range(len(sentences))' loop.
for phrase_index in range(len(which_comma_inside)):
    pattern = re.compile(which_comma_inside[phrase_index])
    whole_text = re.sub(pattern, which_no_comma[phrase_index], whole_text)

terminating_punctuation = "[!?.]"
sentences = [sentence.strip() for sentence in re.split(terminating_punctuation, whole_text)]
for i in range(len(sentences)):
    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')
    #Only perform the substitutions below in the sentences that have a comma/word count ratio below comma_semicolons_threshold, which can be up to 0.2.
    if (sentences_word_counts[i] > 0 and comma_semicolon_count/sentences_word_counts[i] < comma_semicolons_threshold):

        #The indices of the colons and commas will be compared to those of instances of 'that'. Should instances of 'that'
        #be within 20 characters (about 3.5 words+spaces) of a comma or a semicolon, no substitution will take place to introduce further commas.
        commas_semicolons_matches = re.finditer(',|;', sentences[i])
        commas_semicolons_indices_list = [m.start() for m in commas_semicolons_matches]
        #This can get confusing, as I refer to element indexes of lists of indexes. Read the variable titles carefully.
        that_matches = re.finditer('[\s]that[\s]', sentences[i])

        that_indices_list = [m.start() for m in that_matches]
        for that_index in that_indices_list:
            index_difference_list = []
            for punct_index in commas_semicolons_indices_list:
                index_difference_list.append(abs(that_index-punct_index))
            if (all(difference >= 20 for difference in index_difference_list) and (len(sentences[i]) - that_index > 20) and (that_index > 20)):
                #print('\n\nThe "that" at index ' + str(that_index) + ' was over about 3.5 words+spaces of either a comma or a semicolon in sentence and will get a comma.\n\n')
                if that_indices_list.index(that_index) < len(that_indices_list)-1:
                    next_that_index = that_indices_list[that_indices_list.index(that_index)+1]
                    new_sentence = re.sub('[\s]that', ', that', sentences[i][that_index: next_that_index])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:that_index] + new_sentence + sentences[i][next_that_index:]
                    whole_text = whole_text.replace(old_sentence, sentences[i])
                else:
                    new_sentence = re.sub('[\s]that', ', that', sentences[i][that_index:])
                    old_sentence = sentences[i]
                    sentences[i] = sentences[i][:that_index] + new_sentence
                    whole_text = whole_text.replace(old_sentence, sentences[i])
        if sum(commas_semicolons_per_word_for_every_sentence) and len(commas_semicolons_per_word_for_every_sentence) and len(sentences) > 0:
            if (sentences_word_counts[i] > 10 and (comma_semicolon_count/sentences_word_counts[i] > (average_commas_semicolons_per_word_for_whole_text + standard_deviation))):
                set_sentences_many_commas.add(i)
#Since these substitutions are for phrases containing several words, they can be done throughout the "whole_text",
#at the end of a 'for i in range(len(sentences))' loop.
for phrase_index in range(len(that_comma_inside)):
    pattern = re.compile(that_comma_inside[phrase_index])
    whole_text = re.sub(pattern, that_no_comma[phrase_index], whole_text)

whole_text = whole_text.replace(',,,', ',').replace(',,',',').replace(', ,', ',').replace(':,', ':').replace(';,', ';').replace(",',", ",'").replace(',",', ',"')

#All of the data will be outputed in a single dictionary (entireData_dictionaries), whose sole key is mapped to a value consisting of a list of the
#four dictionaries below (along with lists/strings). The title of the individual dictionaries give insight as to the structure of the dictionaries: KeyNames_ValueName1ValueName2ValueName3.
sentencesFewCommas_sentenceIndex = {}
sentencesManyCommas_sentenceIndex = {}
percent_increase_in_commas = {}
potentiallyMispronouncedWords_wordCounts = {}
entireData_dictionaries = {}

#A list of heteronyms in the text will be assembled (using either "heteronyms_list_American_English" or "heteronyms_list_American_English" based on the
#TTS voice you are using (they don't have the exact same list of heteronyms)) Every element of the list will contain the start index of the heteronym
#within the whole_text and the heteronym itself.
if English_Phonetics == "American_English":
    list_of_heteronyms_in_text = []
    for heteronym in heteronyms_list_American_English:
        heteronym_matches = re.finditer("\W" + heteronym + "\W", whole_text)
        list_of_heteronyms_in_text += [[match.start(),heteronym] for match in heteronym_matches]

        heteronym_whole_text = whole_text
        heteronym_matches = re.finditer("\W" + heteronym.lower() + "\W", whole_text)
        list_of_heteronyms_in_text += [[match.start(), heteronym] for match in heteronym_matches]
else:
    list_of_heteronyms_in_text = []
    for heteronym in heteronyms_list_British_English:
        heteronym_matches = re.finditer("\W" + heteronym + "\W", whole_text)
        list_of_heteronyms_in_text += [[match.start(),heteronym] for match in heteronym_matches]

        heteronym_whole_text = whole_text
        heteronym_matches = re.finditer("\W" + heteronym.lower() + "\W", whole_text)
        list_of_heteronyms_in_text += [[match.start(), heteronym] for match in heteronym_matches]

list_of_heteronyms_in_text = sorted(list_of_heteronyms_in_text, key=itemgetter(0))

sentences = [sentence.strip() for sentence in re.split('(!?\.)', whole_text)]
sentence_start_index = 0
set_of_sentence_indices_with_heteronyms = set()
for i in range(len(sentences)):
    #Populating the dictionaries of sentences with few commas and sentences with many commas (this needs to be
    #done before the heteronym substitutions, as the added phoneme tags would lengthen the sentences).
    comma_semicolon_count = sentences[i].count(',') + sentences[i].count(';')
    ##Flag long sentences with less than 2 commas/semicolons (average of 4.7 characters per word in English and sentences shouldn't be longer than 35 words), after having added some commas.
    if ((len(sentences[i].strip()) > 165) and ((sentences[i].count(';') + sentences[i].count(':') + sentences[i].count(',')) < 2)):
        sentencesFewCommas_sentenceIndex[sentences[i] + sentences[i+1]] = i
    if i in set_sentences_many_commas:
        sentencesManyCommas_sentenceIndex[sentences[i] + sentences[i+1]] = i

    #Making a set of sentences indices of sentences containing heteronyms. Only sentences of which the heteronym index within
    #the whole_text is in between the bounds of the sentence's start and end indices within the whole_text are included in the set.
    if list_of_heteronyms_in_text != [] and sentences[i] != "":
        sentence_start_index = whole_text.index(sentences[i], sentence_start_index)
        sentence_end_index = sentence_start_index + len(sentences[i])
        for element in list_of_heteronyms_in_text:
            if element[0]>= sentence_start_index and element[0] < sentence_end_index:
                set_of_sentence_indices_with_heteronyms.add(i)

#All of the sentences at the indices in "set_of_sentence_indices_with_heteronyms" will be merged together and submitted as one block to the code below, for maximal efficiency.
#The sentences will then be split again at "===" placeholder introduced between sentences in combined_sentences and will populate the dictionary
#heteronymListIndex_HeteronymModifiedSentenceHeteronymCount with results.
#This will be repeated for every different heteronym in the text. A space is needed in " ===" to ensure that if the final word in a
#sentence is a heteronym, it will be corretly tokenized by spacy (otherwise, it would give "heteronym===").
combined_sentences = ""
for index in set_of_sentence_indices_with_heteronyms:
    combined_sentences += sentences[index] + " ==="

#Only pass perform parsing of 'text' if a heteronym was found in 'combined_sentences_word_list'. This is important, as the parsing step is very computationally onerous, and there
#may be thousands of heteronyms in the text file.
nlp = spacy.load('en_core_web_lg')
doc = nlp(combined_sentences)
combined_sentences_token_list = [[token.text, token.tag_, token.pos_, token.lemma_, token.children] for token in doc]
combined_sentences_word_list = [i[0] for i in combined_sentences_token_list]

#In certain verb heteronyms, the pronounciation differs for different forms of the verb (transitive vs intransitive).
#The function "is_transitive_verb" returns True if the verb depencency labels marking it as transitive, and
#returns False otherwise.
def is_transitive_verb(combined_sentences_token_list):
    indirect_object = False
    direct_object = False
    #combined_sentences_token_list[4] equates to token.children. indirect_object or direct_object will be set to True
    #if the corresponding dependency labels are present in token.children for the instance of the verb.
    for element in combined_sentences_token_list[4]:
        if type(element) == "generator" and (element.dep_ == "iobj" or element.dep_ == "pobj"):
            indirect_object = True
        elif type(element) == "generator" and (element.dep_ == "dobj" or element.dep_ == "dative"):
            direct_object = True
    #Returns False if the verb is intransitive (indirect_object and direct_object are equal to False).
    #Otherwise returns True, indicating that the verb is transitive.
    if not direct_object and not indirect_object:
        return False
    else:
        return True

#There is a function for every heteronym in 'heteronyms_list_American_English' and 'heteronyms_list_British_English'. In each function, the original
#heteronym is substituted for words with less ambiguous pronunciations, depending on their capitalized status and spacy parsing tagging.
def absent(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Absent" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæbsənt">Absent</phoneme>'
        elif combined_sentences_token_list[i][0] == "absent" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæbsənt">absent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Absent" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="æbˈsɛnt">Absent</phoneme>'
        elif combined_sentences_token_list[i][0] == "absent" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="æbˈsɛnt">absent</phoneme>'
    return combined_sentences_word_list

#In the (seldomly encountered) specific case of the verb "abstract" as in "to summarize", the heteronym should read ˈæbˌstrækt, but in the code below,
#all verb forms of "abstract" have been assigned with the phoneme æbˈstrækt.
def abstract(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Abstract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæbˌstrækt">Abstract</phoneme>'
        elif combined_sentences_token_list[i][0] == "abstract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæbˌstrækt">abstract</phoneme>'
        elif combined_sentences_token_list[i][0] == "Abstract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="æbˈstrækt">Abstract</phoneme>'
        elif combined_sentences_token_list[i][0] == "abstract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="æbˈstrækt">abstract</phoneme>'

        elif combined_sentences_token_list[i][0] == "Abstract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæbstrækt">Abstract</phoneme>'
        elif combined_sentences_token_list[i][0] == "abstract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæbstrækt">abstract</phoneme>'
        elif combined_sentences_token_list[i][0] == "Abstract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="æbˈstrækt">Abstract</phoneme>'
        elif combined_sentences_token_list[i][0] == "abstract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="æbˈstrækt">abstract</phoneme>'
    return combined_sentences_word_list

def abuse(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Abuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈbjuz">Abuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "abuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈbjuz">abuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Abuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈbjus">Abuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "abuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈbjus">abuse</phoneme>'

        elif combined_sentences_token_list[i][0] == "Abuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈbjuːz">Abuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "abuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈbjuːz">abuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Abuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈbjuːs">Abuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "abuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈbjuːs">abuse</phoneme>'
    return combined_sentences_word_list

#Only if the voice is British English, because in American English, it can be pronounced the same (verb vs noun).
def accent(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Accent" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ækˈsɛnt">Accent</phoneme>'
        elif combined_sentences_token_list[i][0] == "accent" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ækˈsɛnt">accent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Accent" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæksənt">Accent</phoneme>'
        elif combined_sentences_token_list[i][0] == "accent" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæksənt">accent</phoneme>'
    return combined_sentences_word_list

def acuminate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Acuminate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈkjuməˌneɪt">Acuminate</phoneme>'
        elif combined_sentences_token_list[i][0] == "acuminate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈkjuməˌneɪt">acuminate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Acuminate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈkjumənɪt">Acuminate</phoneme>'
        elif combined_sentences_token_list[i][0] == "acuminate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈkjumənɪt">acuminate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Acuminate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈkjuːmɪˌneɪt">Acuminate</phoneme>'
        elif combined_sentences_token_list[i][0] == "acuminate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈkjuːmɪˌneɪt">acuminate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Acuminate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈkjuːmɪnɪt">Acuminate</phoneme>'
        elif combined_sentences_token_list[i][0] == "acuminate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈkjuːmɪnɪt">acuminate</phoneme>'
    return combined_sentences_word_list

def addict(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Addict" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈdɪkt">Addict</phoneme>'
        elif combined_sentences_token_list[i][0] == "addict" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈdɪkt">addict</phoneme>'
        elif combined_sentences_token_list[i][0] == "Addict" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædɪkt">Addict</phoneme>'
        elif combined_sentences_token_list[i][0] == "addict" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædɪkt">addict</phoneme>'
    return combined_sentences_word_list

def adduct(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Adduct" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈdʌkt">Adduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "adduct" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈdʌkt">adduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Adduct" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædʌkt">Adduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "adduct" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædʌkt">adduct</phoneme>'
    return combined_sentences_word_list

def adept(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Adept" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈdɛpt">Adept</phoneme>'
        elif combined_sentences_token_list[i][0] == "adept" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈdɛpt">adept</phoneme>'
        elif combined_sentences_token_list[i][0] == "Adept" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædˌɛpt">Adept</phoneme>'
        elif combined_sentences_token_list[i][0] == "adept" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædˌɛpt">adept</phoneme>'
        elif combined_sentences_token_list[i][0] == "Adept" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædɛpt">Adept</phoneme>'
        elif combined_sentences_token_list[i][0] == "adept" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædɛpt">adept</phoneme>'
    return combined_sentences_word_list

def adulterate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Adulterate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈdʌltəˌreɪt">Adulterate</phoneme>'
        elif combined_sentences_token_list[i][0] == "adulterate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈdʌltəˌreɪt">adulterate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Adulterate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈdʌltərɪt">Adulterate</phoneme>'
        elif combined_sentences_token_list[i][0] == "adulterate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈdʌltərɪt">adulterate</phoneme>'
    return combined_sentences_word_list

def advert(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Advert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ədˈvɜrt">Advert</phoneme>'
        elif combined_sentences_token_list[i][0] == "advert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ədˈvɜrt">advert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Advert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædˌvɜrt">Advert</phoneme>'
        elif combined_sentences_token_list[i][0] == "advert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædˌvɜrt">advert</phoneme>'

        elif combined_sentences_token_list[i][0] == "Advert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ədˈvɜːt">Advert</phoneme>'
        elif combined_sentences_token_list[i][0] == "advert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ədˈvɜːt">advert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Advert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædvɜːt">Advert</phoneme>'
        elif combined_sentences_token_list[i][0] == "advert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædvɜːt">advert</phoneme>'
    return combined_sentences_word_list

def advocate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Advocate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædvəˌkeɪt">Advocate</phoneme>'
        elif combined_sentences_token_list[i][0] == "advocate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædvəˌkeɪt">advocate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Advocate" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædvəkɪt">Advocate</phoneme>'
        elif combined_sentences_token_list[i][0] == "advocate" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈædvəkɪt">advocate</phoneme>'
    return combined_sentences_word_list

#In both American and British English, the verb "affect" is pronounced əˈfɛkt. In British English, the noun may be
#pronounced as either ˈæfɛkt or əˈfɛkt and in American English, the noun is pronounced ˈæfˌɛkt, so the SSML phoneme
#is only included for the noun in American English.
def affect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Affect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈfɛkt">Affect</phoneme>'
        elif combined_sentences_token_list[i][0] == "affect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈfɛkt">affect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Affect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæfɛkt">Affect</phoneme>'
        elif combined_sentences_token_list[i][0] == "affect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæfɛkt">affect</phoneme>'
    return combined_sentences_word_list

def affiliate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Affiliate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈfɪliˌeɪt">Affiliate</phoneme>'
        elif combined_sentences_token_list[i][0] == "affiliate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈfɪliˌeɪt">affiliate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Affiliate" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈfɪliɪt">Affiliate</phoneme>'
        elif combined_sentences_token_list[i][0] == "affiliate" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈfɪliɪt">affiliate</phoneme>'
    return combined_sentences_word_list

def affix(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Affix" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈfɪks">Affix</phoneme>'
        elif combined_sentences_token_list[i][0] == "affix" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈfɪks">affix</phoneme>'
        elif combined_sentences_token_list[i][0] == "Affix" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæfˌɪks">Affix</phoneme>'
        elif combined_sentences_token_list[i][0] == "affix" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæfˌɪks">affix</phoneme>'

        elif combined_sentences_token_list[i][0] == "Affix" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈfɪks">Affix</phoneme>'
        elif combined_sentences_token_list[i][0] == "affix" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈfɪks">affix</phoneme>'
        elif combined_sentences_token_list[i][0] == "Affix" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæfɪks">Affix</phoneme>'
        elif combined_sentences_token_list[i][0] == "affix" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæfɪks">affix</phoneme>'
    return combined_sentences_word_list

def agglomerate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Agglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈglɑmərˌeɪt">Agglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "agglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈglɑmərˌeɪt">agglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Agglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈɡlɒmərɪt">Agglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "agglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈɡlɒmərɪt">agglomerate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Agglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈɡlɒməˌreɪt">Agglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "agglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈɡlɒməˌreɪt">agglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Agglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈɡlɒmərɪt">Agglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "agglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈɡlɒmərɪt">agglomerate</phoneme>'
    return combined_sentences_word_list

def agglutinate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Agglutinate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈɡluːtɪˌneɪt">Agglutinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "agglutinate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈɡluːtɪˌneɪt">agglutinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Agglutinate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈɡluːtɪnɪt">Agglutinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "agglutinate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈɡluːtɪnɪt">agglutinate</phoneme>'
    return combined_sentences_word_list


def aggregate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Aggregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈægrəˌgeɪt">Aggregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aggregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈægrəˌgeɪt">aggregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Aggregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈægrəgɪt">Aggregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aggregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈægrəgɪt">aggregate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Aggregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæɡrɪˌɡeɪt">Aggregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aggregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæɡrɪˌɡeɪt">aggregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Aggregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæɡrɪɡɪt">Aggregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aggregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæɡrɪɡɪt">aggregate</phoneme>'
    return combined_sentences_word_list

def aliment(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Aliment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæləˌmɛnt">Aliment</phoneme>'
        elif combined_sentences_token_list[i][0] == "aliment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæləˌmɛnt">aliment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Aliment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæləmənt">Aliment</phoneme>'
        elif combined_sentences_token_list[i][0] == "aliment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæləmənt">aliment</phoneme>'

        elif combined_sentences_token_list[i][0] == "Aliment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈælɪˌmɛnt">Aliment</phoneme>'
        elif combined_sentences_token_list[i][0] == "aliment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈælɪˌmɛnt">aliment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Aliment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈælɪmənt">Aliment</phoneme>'
        elif combined_sentences_token_list[i][0] == "aliment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈælɪmənt">aliment</phoneme>'
    return combined_sentences_word_list

def alloy(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Alloy" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈlɔɪ">Alloy</phoneme>'
        elif combined_sentences_token_list[i][0] == "alloy" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈlɔɪ">alloy</phoneme>'
        elif combined_sentences_token_list[i][0] == "Alloy" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈælɔɪ">Alloy</phoneme>'
        elif combined_sentences_token_list[i][0] == "alloy" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈælɔɪ">alloy</phoneme>'
    return combined_sentences_word_list

#Spacy tokenizes "Allies" (as in "the Allied forces") as a proper name.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def allied(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Allied" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈlaɪd">Allied</phoneme>'
        elif combined_sentences_token_list[i][0] == "allied" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈlaɪd">allied</phoneme>'
        elif combined_sentences_token_list[i][0] == "Allied" and combined_sentences_token_list[i][1] in ["NNP", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈælaɪd">Allied</phoneme>'
        elif combined_sentences_token_list[i][0] == "allied" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈælaɪd">allied</phoneme>'
    return combined_sentences_word_list

def ally(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Ally" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈlaɪ">Ally</phoneme>'
        elif combined_sentences_token_list[i][0] == "ally" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈlaɪ">ally</phoneme>'
        elif combined_sentences_token_list[i][0] == "Ally" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈælaɪ">Ally</phoneme>'
        elif combined_sentences_token_list[i][0] == "ally" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈælaɪ">ally</phoneme>'
    return combined_sentences_word_list

def alternate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Alternate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɔltərˌneɪt">Alternate</phoneme>'
        elif combined_sentences_token_list[i][0] == "alternate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɔltərˌneɪt">alternate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Alternate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɔltərnɪt">Alternate</phoneme>'
        elif combined_sentences_token_list[i][0] == "alternate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɔltərnɪt">alternate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Alternate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɔːltəˌneɪt">Alternate</phoneme>'
        elif combined_sentences_token_list[i][0] == "alternate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɔːltəˌneɪt">alternate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Alternate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɔːlˈtɜːnɪt">Alternate</phoneme>'
        elif combined_sentences_token_list[i][0] == "alternate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɔːlˈtɜːnɪt">alternate</phoneme>'
    return combined_sentences_word_list

def analyses(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Analyses" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈænəlaɪzɪz">Analyses</phoneme>'
        elif combined_sentences_token_list[i][0] == "analyses" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈænəlaɪzɪz">analyses</phoneme>'
        elif combined_sentences_token_list[i][0] == "Analyses" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈnælɪsiːz">Analyses</phoneme>'
        elif combined_sentences_token_list[i][0] == "analyses" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈnælɪsiːz">analyses</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def animate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Animate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈænɪˌmeɪt">Animate</phoneme>'
        elif combined_sentences_token_list[i][0] == "animate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈænɪˌmeɪt">animate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Animate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈænəmɪt">Animate</phoneme>'
        elif combined_sentences_token_list[i][0] == "animate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈænəmɪt">animate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Animate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈænɪˌmeɪt">Animate</phoneme>'
        elif combined_sentences_token_list[i][0] == "animate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈænɪˌmeɪt">animate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Animate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈænɪmɪt">Animate</phoneme>'
        elif combined_sentences_token_list[i][0] == "animate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈænɪmɪt">animate</phoneme>'
    return combined_sentences_word_list

def annex(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Annex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="æˈnɛks">Annex</phoneme>'
        elif combined_sentences_token_list[i][0] == "annex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="æˈnɛks">annex</phoneme>'
        elif combined_sentences_token_list[i][0] == "Annex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈænˌɛks">Annex</phoneme>'
        elif combined_sentences_token_list[i][0] == "annex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈænˌɛks">annex</phoneme>'

        elif combined_sentences_token_list[i][0] == "Annex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="æˈnɛks">Annex</phoneme>'
        elif combined_sentences_token_list[i][0] == "annex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="æˈnɛks">annex</phoneme>'
        elif combined_sentences_token_list[i][0] == "Annex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈænɛks">Annex</phoneme>'
        elif combined_sentences_token_list[i][0] == "annex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈænɛks">annex</phoneme>'
    return combined_sentences_word_list

def appropriate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Appropriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈproʊpriˌeɪt">Appropriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "appropriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈproʊpriˌeɪt">appropriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Appropriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈproʊpriɪt">Appropriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "appropriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈproʊpriɪt">appropriate</phoneme>'

        if combined_sentences_token_list[i][0] == "Appropriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈprəʊprɪˌeɪt">Appropriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "appropriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈprəʊprɪˌeɪt">appropriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Appropriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈprəʊprɪɪt">Appropriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "appropriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈprəʊprɪɪt">appropriate</phoneme>'
    return combined_sentences_word_list

def approximate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Approximate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈprɑksəˌmeɪt">Approximate</phoneme>'
        elif combined_sentences_token_list[i][0] == "approximate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈprɑksəˌmeɪt">approximate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Approximate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈprɑksəmɪt">Approximate</phoneme>'
        elif combined_sentences_token_list[i][0] == "approximate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈprɑksəmɪt">approximate</phoneme>'

        if combined_sentences_token_list[i][0] == "Approximate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈprɒksɪˌmeɪt">Approximate</phoneme>'
        elif combined_sentences_token_list[i][0] == "approximate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈprɒksɪˌmeɪt">approximate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Approximate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈprɒksɪmɪt">Approximate</phoneme>'
        elif combined_sentences_token_list[i][0] == "approximate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈprɒksɪmɪt">approximate</phoneme>'
    return combined_sentences_word_list

def arithmetic(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Arithmetic" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈrɪθmətɪk">Arithmetic</phoneme>'
        elif combined_sentences_token_list[i][0] == "arithmetic" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈrɪθmətɪk">arithmetic</phoneme>'
        elif combined_sentences_token_list[i][0] == "Arithmetic" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌærɪθˈmɛtɪk">Arithmetic</phoneme>'
        elif combined_sentences_token_list[i][0] == "arithmetic" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌærɪθˈmɛtɪk">arithmetic</phoneme>'
    return combined_sentences_word_list

def articulate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Articulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɑrˈtɪkjəˌleɪt">Articulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "articulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɑrˈtɪkjəˌleɪt">articulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Articulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɑrˈtɪkjəlɪt">Articulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "articulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɑrˈtɪkjəlɪt">articulate</phoneme>'

        if combined_sentences_token_list[i][0] == "Articulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɑːˈtɪkjʊˌleɪt">Articulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "articulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɑːˈtɪkjʊˌleɪt">articulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Articulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɑːˈtɪkjʊlɪt">Articulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "articulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɑːˈtɪkjʊlɪt">articulate</phoneme>'
    return combined_sentences_word_list

def aspirate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Aspirate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæspəˌreɪt">Aspirate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aspirate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæspəˌreɪt">aspirate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Aspirate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæspərɪt">Aspirate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aspirate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæspərɪt">aspirate</phoneme>'

        if combined_sentences_token_list[i][0] == "Aspirate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæspɪˌreɪt">Aspirate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aspirate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæspɪˌreɪt">aspirate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Aspirate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæspɪrɪt">Aspirate</phoneme>'
        elif combined_sentences_token_list[i][0] == "aspirate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæspɪrɪt">aspirate</phoneme>'
    return combined_sentences_word_list

def associate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Associate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈsoʊʃiˌeɪt">Associate</phoneme>'
        elif combined_sentences_token_list[i][0] == "associate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈsoʊʃiˌeɪt">associate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Associate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈsoʊʃiɪt">Associate</phoneme>'
        elif combined_sentences_token_list[i][0] == "associate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈsoʊʃiɪt">associate</phoneme>'

        if combined_sentences_token_list[i][0] == "Associate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈsəʊʃɪˌeɪt">Associate</phoneme>'
        elif combined_sentences_token_list[i][0] == "associate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈsəʊʃɪˌeɪt">associate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Associate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈsəʊʃɪɪt">Associate</phoneme>'
        elif combined_sentences_token_list[i][0] == "associate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈsəʊʃɪɪt">associate</phoneme>'
    return combined_sentences_word_list

def attribute(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Attribute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈtrɪbjut">Attribute</phoneme>'
        elif combined_sentences_token_list[i][0] == "attribute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈtrɪbjut">attribute</phoneme>'
        elif combined_sentences_token_list[i][0] == "Attribute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈætrəˌbjut">Attribute</phoneme>'
        elif combined_sentences_token_list[i][0] == "attribute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈætrəˌbjut">attribute</phoneme>'

        elif combined_sentences_token_list[i][0] == "Attribute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈtrɪbjuːt">Attribute</phoneme>'
        elif combined_sentences_token_list[i][0] == "attribute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əˈtrɪbjuːt">attribute</phoneme>'
        elif combined_sentences_token_list[i][0] == "Attribute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈætrɪˌbjuːt">Attribute</phoneme>'
        elif combined_sentences_token_list[i][0] == "attribute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈætrɪˌbjuːt">attribute</phoneme>'
    return combined_sentences_word_list

def augment(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Augment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɔgˈmɛnt">Augment</phoneme>'
        elif combined_sentences_token_list[i][0] == "augment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɔgˈmɛnt">augment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Augment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɔgˌmɛnt">Augment</phoneme>'
        elif combined_sentences_token_list[i][0] == "augment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɔgˌmɛnt">augment</phoneme>'

        elif combined_sentences_token_list[i][0] == "Augment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɔːɡˈmɛnt">Augment</phoneme>'
        elif combined_sentences_token_list[i][0] == "augment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɔːɡˈmɛnt">augment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Augment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɔːɡmɛnt">Augment</phoneme>'
        elif combined_sentences_token_list[i][0] == "augment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɔːɡmɛnt">augment</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def august(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "August" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɔˈgʌst">August</phoneme>'
        elif combined_sentences_token_list[i][0] == "august" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɔˈgʌst">august</phoneme>'
        elif combined_sentences_token_list[i][0] == "August" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɔgəst">August</phoneme>'
        elif combined_sentences_token_list[i][0] == "august" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɔgəst">august</phoneme>'

        elif combined_sentences_token_list[i][0] == "August" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɔːˈɡʌst">August</phoneme>'
        elif combined_sentences_token_list[i][0] == "august" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɔːˈɡʌst">august</phoneme>'
        elif combined_sentences_token_list[i][0] == "August" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɔːɡəst">August</phoneme>'
        elif combined_sentences_token_list[i][0] == "august" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɔːɡəst">august</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def axes(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Axes" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() in ["ax", "axe"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈækˌsɪz">Axes</phoneme>'
        elif combined_sentences_token_list[i][0] == "axes" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() in ["ax", "axe"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈækˌsɪz">axes</phoneme>'
        elif combined_sentences_token_list[i][0] == "Axes" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() == "axis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈækˌsiz">Axes</phoneme>'
        elif combined_sentences_token_list[i][0] == "axes" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() == "axis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈækˌsiz">axes</phoneme>'

        if combined_sentences_token_list[i][0] == "Axes" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() in ["ax", "axe"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæksɪz">Axes</phoneme>'
        elif combined_sentences_token_list[i][0] == "axes" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() in ["ax", "axe"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæksɪz">axes</phoneme>'
        elif combined_sentences_token_list[i][0] == "Axes" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() == "axis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæksiːz">Axes</phoneme>'
        elif combined_sentences_token_list[i][0] == "axes" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() == "axis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈæksiːz">axes</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def bases(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Bases" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() == "base":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈbeɪsɪz">Bases</phoneme>'
        elif combined_sentences_token_list[i][0] == "bases" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() == "base":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈbeɪsɪz">bases</phoneme>'
        elif combined_sentences_token_list[i][0] == "Bases" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() == "basis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈbeɪˌsiz">Bases</phoneme>'
        elif combined_sentences_token_list[i][0] == "bases" and English_Phonetics == "American_English" and combined_sentences_token_list[i][3].lower() == "basis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈbeɪˌsiz">bases</phoneme>'

        elif combined_sentences_token_list[i][0] == "Bases" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() == "base":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈbeɪsɪz">Bases</phoneme>'
        elif combined_sentences_token_list[i][0] == "bases" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() == "base":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈbeɪsɪz">bases</phoneme>'
        elif combined_sentences_token_list[i][0] == "Bases" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() == "basis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈbeɪsiːz">Bases</phoneme>'
        elif combined_sentences_token_list[i][0] == "bases" and English_Phonetics == "British_English" and combined_sentences_token_list[i][3].lower() == "basis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈbeɪsiːz">bases</phoneme>'
    return combined_sentences_word_list

#As the following nouns may be pronounced "baʊ" for a bow gesture or the forward end of a ship and "boʊ" or "bəʊ" for a bow-shaped object,
#only the verb (always pronounced "baʊ") is included here to avoid misassigning the phonemes.
def bow(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Bow" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈbaʊ">Bow</phoneme>'
        elif combined_sentences_token_list[i][0] == "bow" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈbaʊ">bow</phoneme>'
    return combined_sentences_word_list

def bows(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Bows" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈbaʊz">Bows</phoneme>'
        elif combined_sentences_token_list[i][0] == "bows" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈbaʊz">bows</phoneme>'
        elif combined_sentences_token_list[i][0] == "Bows" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈboʊz">Bows</phoneme>'
        elif combined_sentences_token_list[i][0] == "bows" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈboʊz">bows</phoneme>'
    return combined_sentences_word_list

#As there are several pronounciations for the different nouns "buffet", only the verb was included.
def buffet(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Buffet" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈbʌfɪt">Buffet</phoneme>'
        elif combined_sentences_token_list[i][0] == "buffet" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈbʌfɪt">buffet</phoneme>'
    return combined_sentences_word_list

def certificate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Certificate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="sərˈtɪfɪˌkeɪt">Certificate</phoneme>'
        elif combined_sentences_token_list[i][0] == "certificate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="sərˈtɪfɪˌkeɪt">certificate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Certificate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="sərˈtɪfɪkɪt">Certificate</phoneme>'
        elif combined_sentences_token_list[i][0] == "certificate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="sərˈtɪfɪkɪt">certificate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Certificate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈtɪfɪˌkeɪt">Certificate</phoneme>'
        elif combined_sentences_token_list[i][0] == "certificate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈtɪfɪˌkeɪt">certificate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Certificate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈtɪfɪkɪt">Certificate</phoneme>'
        elif combined_sentences_token_list[i][0] == "certificate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈtɪfɪkɪt">certificate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def chassis(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Chassis" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:3] == "NNS":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈʃæsˌiz">Chassis</phoneme>'
        elif combined_sentences_token_list[i][0] == "chassis" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:3] == "NNS":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈʃæsˌiz">chassis</phoneme>'
        elif combined_sentences_token_list[i][0] == "Chassis" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈʃæsi">Chassis</phoneme>'
        elif combined_sentences_token_list[i][0] == "chassis" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈʃæsi">chassis</phoneme>'

        elif combined_sentences_token_list[i][0] == "Chassis" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:3] == "NNS":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈʃæsɪz">Chassis</phoneme>'
        elif combined_sentences_token_list[i][0] == "chassis" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:3] == "NNS":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈʃæsɪz">chassis</phoneme>'
        elif combined_sentences_token_list[i][0] == "Chassis" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈʃæsɪ">Chassis</phoneme>'
        elif combined_sentences_token_list[i][0] == "chassis" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈʃæsɪ">chassis</phoneme>'
    return combined_sentences_word_list

def close(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Close" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kloʊz">Close</phoneme>'
        elif combined_sentences_token_list[i][0] == "close" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kloʊz">close</phoneme>'
        elif combined_sentences_token_list[i][0] == "Close" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kloʊs">Close</phoneme>'
        elif combined_sentences_token_list[i][0] == "close" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kloʊs">close</phoneme>'

        elif combined_sentences_token_list[i][0] == "Close" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kləʊz">Close</phoneme>'
        elif combined_sentences_token_list[i][0] == "close" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kləʊz">close</phoneme>'
        elif combined_sentences_token_list[i][0] == "Close" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kləʊs">Close</phoneme>'
        elif combined_sentences_token_list[i][0] == "close" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kləʊs">close</phoneme>'
    return combined_sentences_word_list

def coagulate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Coagulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="koʊˈægjuˌleɪt">Coagulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coagulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="koʊˈægjuˌleɪt">coagulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Coagulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="koʊˈægjulit">Coagulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coagulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="koʊˈægjulit">coagulate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Coagulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəʊˈæɡjʊˌleɪt">Coagulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coagulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəʊˈæɡjʊˌleɪt">coagulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Coagulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəʊˈæɡjʊlɪt">Coagulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coagulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəʊˈæɡjʊlɪt">coagulate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def coax(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Coax" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="koʊks">Coax</phoneme>'
        elif combined_sentences_token_list[i][0] == "coax" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="koʊks">coax</phoneme>'
        elif combined_sentences_token_list[i][0] == "Coax" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kouˈæks">Coax</phoneme>'
        elif combined_sentences_token_list[i][0] == "coax" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kouˈæks">coax</phoneme>'

        elif combined_sentences_token_list[i][0] == "Coax" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəʊks">Coax</phoneme>'
        elif combined_sentences_token_list[i][0] == "coax" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəʊks">coax</phoneme>'
        elif combined_sentences_token_list[i][0] == "Coax" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkəʊæks">Coax</phoneme>'
        elif combined_sentences_token_list[i][0] == "coax" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkəʊæks">coax</phoneme>'
    return combined_sentences_word_list

#As distinct "collect" nouns can be pronounced differently, only the verb was included
def collect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Collect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəˈlɛkt">Collect</phoneme>'
        elif combined_sentences_token_list[i][0] == "collect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəˈlɛkt">collect</phoneme>'
    return combined_sentences_word_list

def combat(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Combat" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkʌmˌbæt">Combat</phoneme>'
        elif combined_sentences_token_list[i][0] == "combat" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkʌmˌbæt">combat</phoneme>'
        elif combined_sentences_token_list[i][0] == "Combat" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑmˌbæt">Combat</phoneme>'
        elif combined_sentences_token_list[i][0] == "combat" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑmˌbæt">combat</phoneme>'

        elif combined_sentences_token_list[i][0] == "Combat" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəmˈbæt">Combat</phoneme>'
        elif combined_sentences_token_list[i][0] == "combat" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəmˈbæt">combat</phoneme>'
        elif combined_sentences_token_list[i][0] == "Combat" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒmbæt">Combat</phoneme>'
        elif combined_sentences_token_list[i][0] == "combat" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒmbæt">combat</phoneme>'
    return combined_sentences_word_list

#The verb "combine" is pronounced the same in American and British English, except for the form involving harvesting crops with a combine harvester
#(which is pronounced like the noun in American English). Therefore, only the nouns are included.
def combine(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Combine" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑmˌbaɪn">Combine</phoneme>'
        elif combined_sentences_token_list[i][0] == "combine" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑmˌbaɪn">combine</phoneme>'
        elif combined_sentences_token_list[i][0] == "Combine" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒmbaɪn">Combine</phoneme>'
        elif combined_sentences_token_list[i][0] == "combine" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒmbaɪn">combine</phoneme>'
    return combined_sentences_word_list

def commune(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Commune" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəˈmjun">Commune</phoneme>'
        elif combined_sentences_token_list[i][0] == "commune" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəˈmjun">commune</phoneme>'
        elif combined_sentences_token_list[i][0] == "Commune" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑmˌjun">Commune</phoneme>'
        elif combined_sentences_token_list[i][0] == "commune" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑmˌjun">commune</phoneme>'

        elif combined_sentences_token_list[i][0] == "Commune" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəˈmjuːn">Commune</phoneme>'
        elif combined_sentences_token_list[i][0] == "commune" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəˈmjuːn">commune</phoneme>'
        elif combined_sentences_token_list[i][0] == "Commune" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒmjuːn">Commune</phoneme>'
        elif combined_sentences_token_list[i][0] == "commune" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒmjuːn">commune</phoneme>'
    return combined_sentences_word_list

def compact(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Compact" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəmˈpækt">Compact</phoneme>'
        elif combined_sentences_token_list[i][0] == "compact" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəmˈpækt">compact</phoneme>'
        elif combined_sentences_token_list[i][0] == "Compact" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑmpækt">Compact</phoneme>'
        elif combined_sentences_token_list[i][0] == "compact" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑmpækt">compact</phoneme>'
    return combined_sentences_word_list

#Only if the voice is American English, because in British English, it is pronounced the same. Also, only the noun
#is included ("ˈkɑmˌplɛks"), as the adjective may or may not be pronounced the same as the noun.
def complex(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Complex" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑmˌplɛks">Complex</phoneme>'
        elif combined_sentences_token_list[i][0] == "complex" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑmˌplɛks">complex</phoneme>'
    return combined_sentences_word_list

def compound(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Compound" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəmˈpaʊnd">Compound</phoneme>'
        elif combined_sentences_token_list[i][0] == "compound" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəmˈpaʊnd">compound</phoneme>'
        elif combined_sentences_token_list[i][0] == "Compound" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑmˌpaʊnd">Compound</phoneme>'
        elif combined_sentences_token_list[i][0] == "compound" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑmˌpaʊnd">compound</phoneme>'

        elif combined_sentences_token_list[i][0] == "Compound" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəmˈpaʊnd">Compound</phoneme>'
        elif combined_sentences_token_list[i][0] == "compound" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəmˈpaʊnd">compound</phoneme>'
        elif combined_sentences_token_list[i][0] == "Compound" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒmpaʊnd">Compound</phoneme>'
        elif combined_sentences_token_list[i][0] == "compound" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒmpaʊnd">compound</phoneme>'
    return combined_sentences_word_list

def compress(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Compress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəmˈprɛs">Compress</phoneme>'
        elif combined_sentences_token_list[i][0] == "compress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəmˈprɛs">compress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Compress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑmˌprɛs">Compress</phoneme>'
        elif combined_sentences_token_list[i][0] == "compress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑmˌprɛs">compress</phoneme>'

        elif combined_sentences_token_list[i][0] == "Compress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəmˈprɛs">Compress</phoneme>'
        elif combined_sentences_token_list[i][0] == "compress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəmˈprɛs">compress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Compress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒmprɛs">Compress</phoneme>'
        elif combined_sentences_token_list[i][0] == "compress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒmprɛs">compress</phoneme>'
    return combined_sentences_word_list

def concert(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Concert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsɜrt">Concert</phoneme>'
        elif combined_sentences_token_list[i][0] == "concert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsɜrt">concert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Concert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnsərt">Concert</phoneme>'
        elif combined_sentences_token_list[i][0] == "concert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnsərt">concert</phoneme>'

        elif combined_sentences_token_list[i][0] == "Concert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsɜːt">Concert</phoneme>'
        elif combined_sentences_token_list[i][0] == "concert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsɜːt">concert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Concert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnsɜːt">Concert</phoneme>'
        elif combined_sentences_token_list[i][0] == "concert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnsɜːt">concert</phoneme>'
    return combined_sentences_word_list

#Only in American English, as the noun, verb and adjective are pronounced the same in British English.
#Also, as some distinct "concrete" verbs are pronounced differently, only the noun and adjective are included.
def concrete(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Concrete" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌkrit">Concrete</phoneme>'
        elif combined_sentences_token_list[i][0] == "concrete" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌkrit">concrete</phoneme>'
    return combined_sentences_word_list

def conduct(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Conduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈdʌkt">Conduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "conduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈdʌkt">conduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑndəkt">Conduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "conduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑndəkt">conduct</phoneme>'

        elif combined_sentences_token_list[i][0] == "Conduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈdʌkt">Conduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "conduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈdʌkt">conduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒndʌkt">Conduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "conduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒndʌkt">conduct</phoneme>'
    return combined_sentences_word_list

def confect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Confect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈfɛkt">Confect</phoneme>'
        elif combined_sentences_token_list[i][0] == "confect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈfɛkt">confect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Confect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnfekt">Confect</phoneme>'
        elif combined_sentences_token_list[i][0] == "confect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnfekt">confect</phoneme>'
    return combined_sentences_word_list

def confines(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Confines" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈfaɪnz">Confines</phoneme>'
        elif combined_sentences_token_list[i][0] == "confines" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈfaɪnz">confines</phoneme>'
        elif combined_sentences_token_list[i][0] == "Confines" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnfaɪnz">Confines</phoneme>'
        elif combined_sentences_token_list[i][0] == "confines" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnfaɪnz">confines</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def conflict(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Conflict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈflɪkt">Conflict</phoneme>'
        elif combined_sentences_token_list[i][0] == "conflict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈflɪkt">conflict</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conflict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌflɪkt">Conflict</phoneme>'
        elif combined_sentences_token_list[i][0] == "conflict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌflɪkt">conflict</phoneme>'

        elif combined_sentences_token_list[i][0] == "Conflict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈflɪkt">Conflict</phoneme>'
        elif combined_sentences_token_list[i][0] == "conflict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈflɪkt">conflict</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conflict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnflɪkt">Conflict</phoneme>'
        elif combined_sentences_token_list[i][0] == "conflict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnflɪkt">conflict</phoneme>'
    return combined_sentences_word_list

def conglomerate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Conglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈglɑmərˌeɪt">Conglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈglɑmərˌeɪt">conglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈglɑmərɪt">Conglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conglomerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈglɑmərɪt">conglomerate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Conglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈɡlɒməˌreɪt">Conglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈɡlɒməˌreɪt">conglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈɡlɒmərɪt">Conglomerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conglomerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈɡlɒmərɪt">conglomerate</phoneme>'
    return combined_sentences_word_list

def congregate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Congregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑngrəˌgeɪt">Congregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "congregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑngrəˌgeɪt">congregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Congregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑngrəgɪt">Congregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "congregate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑngrəgɪt">congregate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Congregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒŋɡrɪˌɡeɪt">Congregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "congregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒŋɡrɪˌɡeɪt">congregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Congregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒŋɡrɪɡɪt">Congregate</phoneme>'
        elif combined_sentences_token_list[i][0] == "congregate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒŋɡrɪɡɪt">congregate</phoneme>'
    return combined_sentences_word_list

def congress(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Congress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈɡres">Congress</phoneme>'
        elif combined_sentences_token_list[i][0] == "congress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈɡres">congress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Congress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑngrɪs">Congress</phoneme>'
        elif combined_sentences_token_list[i][0] == "congress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑngrɪs">congress</phoneme>'

        elif combined_sentences_token_list[i][0] == "Congress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈɡres">Congress</phoneme>'
        elif combined_sentences_token_list[i][0] == "congress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈɡres">congress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Congress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒŋɡrɛs">Congress</phoneme>'
        elif combined_sentences_token_list[i][0] == "congress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒŋɡrɛs">congress</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def conjugate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Conjugate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑndʒəˌgeɪt">Conjugate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conjugate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑndʒəˌgeɪt">conjugate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conjugate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑndʒəgət">Conjugate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conjugate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑndʒəgət">conjugate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Conjugate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒndʒʊˌɡeɪt">Conjugate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conjugate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒndʒʊˌɡeɪt">conjugate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conjugate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒndʒʊɡɪt">Conjugate</phoneme>'
        elif combined_sentences_token_list[i][0] == "conjugate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒndʒʊɡɪt">conjugate</phoneme>'
    return combined_sentences_word_list

def conscript(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Conscript" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈskrɪpt">Conscript</phoneme>'
        elif combined_sentences_token_list[i][0] == "conscript" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈskrɪpt">conscript</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conscript" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌskrɪpt">Conscript</phoneme>'
        elif combined_sentences_token_list[i][0] == "conscript" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌskrɪpt">conscript</phoneme>'

        elif combined_sentences_token_list[i][0] == "Conscript" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈskrɪpt">Conscript</phoneme>'
        elif combined_sentences_token_list[i][0] == "conscript" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈskrɪpt">conscript</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conscript" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnskrɪpt">Conscript</phoneme>'
        elif combined_sentences_token_list[i][0] == "conscript" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnskrɪpt">conscript</phoneme>'
    return combined_sentences_word_list

#Only in American English, as they can be pronounced the same in British English, whereas the noun is usually "ˈkɑnˌsɜrv" in American English.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def conserve(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Conserve" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsɜrv">Conserve</phoneme>'
        elif combined_sentences_token_list[i][0] == "conserve" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsɜrv">conserve</phoneme>'
        elif combined_sentences_token_list[i][0] == "Conserve" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌsɜrv">Conserve</phoneme>'
        elif combined_sentences_token_list[i][0] == "conserve" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌsɜrv">conserve</phoneme>'
    return combined_sentences_word_list

def consociate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Consociate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsoʊʃiˌeɪt">Consociate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consociate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsoʊʃiˌeɪt">consociate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Consociate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsoʊʃiɪt">Consociate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consociate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsoʊʃiɪt">consociate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Consociate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsəʊʃɪˌeɪt">Consociate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consociate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsəʊʃɪˌeɪt">consociate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Consociate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsəʊʃɪɪt">Consociate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consociate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsəʊʃɪɪt">consociate</phoneme>'
    return combined_sentences_word_list

def console(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Console" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsoʊl">Console</phoneme>'
        elif combined_sentences_token_list[i][0] == "console" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsoʊl">console</phoneme>'
        elif combined_sentences_token_list[i][0] == "Console" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌsoʊl">Console</phoneme>'
        elif combined_sentences_token_list[i][0] == "console" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌsoʊl">console</phoneme>'

        elif combined_sentences_token_list[i][0] == "Console" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsəʊl">Console</phoneme>'
        elif combined_sentences_token_list[i][0] == "console" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsəʊl">console</phoneme>'
        elif combined_sentences_token_list[i][0] == "Console" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnsəʊl">Console</phoneme>'
        elif combined_sentences_token_list[i][0] == "console" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnsəʊl">console</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def consort(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Consort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsɔrt">Consort</phoneme>'
        elif combined_sentences_token_list[i][0] == "consort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsɔrt">consort</phoneme>'
        elif combined_sentences_token_list[i][0] == "Consort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌsɔrt">Consort</phoneme>'
        elif combined_sentences_token_list[i][0] == "consort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌsɔrt">consort</phoneme>'

        elif combined_sentences_token_list[i][0] == "Consort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsɔːt">Consort</phoneme>'
        elif combined_sentences_token_list[i][0] == "consort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsɔːt">consort</phoneme>'
        elif combined_sentences_token_list[i][0] == "Consort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnsɔːt">Consort</phoneme>'
        elif combined_sentences_token_list[i][0] == "consort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnsɔːt">consort</phoneme>'
    return combined_sentences_word_list

def construct(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Construct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈstrʌkt">Construct</phoneme>'
        elif combined_sentences_token_list[i][0] == "construct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈstrʌkt">construct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Construct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌstrʌkt">Construct</phoneme>'
        elif combined_sentences_token_list[i][0] == "construct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌstrʌkt">construct</phoneme>'

        elif combined_sentences_token_list[i][0] == "Construct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈstrʌkt">Construct</phoneme>'
        elif combined_sentences_token_list[i][0] == "construct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈstrʌkt">construct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Construct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnstrʌkt">Construct</phoneme>'
        elif combined_sentences_token_list[i][0] == "construct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnstrʌkt">construct</phoneme>'
    return combined_sentences_word_list

def consummate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Consummate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnsəˌmeɪt">Consummate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consummate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnsəˌmeɪt">consummate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Consummate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsʌmɪt">Consummate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consummate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsʌmɪt">consummate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Consummate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnsəˌmeɪt">Consummate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consummate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnsəˌmeɪt">consummate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Consummate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsʌmɪt">Consummate</phoneme>'
        elif combined_sentences_token_list[i][0] == "consummate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈsʌmɪt">consummate</phoneme>'
    return combined_sentences_word_list

#As there are several different ways to pronounce the distinct nouns "content", only the adjective and verb are included
def content(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Content" and combined_sentences_token_list[i][1][:2] in ["JJ", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈtɛnt">Content</phoneme>'
        elif combined_sentences_token_list[i][0] == "content" and combined_sentences_token_list[i][1][:2] in ["JJ", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈtɛnt">content</phoneme>'
    return combined_sentences_word_list

def contest(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Contest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈtɛst">Contest</phoneme>'
        elif combined_sentences_token_list[i][0] == "contest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈtɛst">contest</phoneme>'
        elif combined_sentences_token_list[i][0] == "Contest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌtɛst">Contest</phoneme>'
        elif combined_sentences_token_list[i][0] == "contest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌtɛst">contest</phoneme>'

        elif combined_sentences_token_list[i][0] == "Contest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈtɛst">Contest</phoneme>'
        elif combined_sentences_token_list[i][0] == "contest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈtɛst">contest</phoneme>'
        elif combined_sentences_token_list[i][0] == "Contest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒntɛst">Contest</phoneme>'
        elif combined_sentences_token_list[i][0] == "contest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒntɛst">contest</phoneme>'
    return combined_sentences_word_list

#In American English, different versions of the verb "contract" have distinct pronounciations, while that is not the case in British English.
#Consequently, only the noun and adjective are included for American English.
def contract(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Contract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑntrækt">Contract</phoneme>'
        elif combined_sentences_token_list[i][0] == "contract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑntrækt">contract</phoneme>'

        elif combined_sentences_token_list[i][0] == "Contract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈtrækt">Contract</phoneme>'
        elif combined_sentences_token_list[i][0] == "contract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈtrækt">contract</phoneme>'
        elif combined_sentences_token_list[i][0] == "Contract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒntrækt">Contract</phoneme>'
        elif combined_sentences_token_list[i][0] == "contract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒntrækt">contract</phoneme>'
    return combined_sentences_word_list

def contrast(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Contrast" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈtræst">Contrast</phoneme>'
        elif combined_sentences_token_list[i][0] == "contrast" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈtræst">contrast</phoneme>'
        elif combined_sentences_token_list[i][0] == "Contrast" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌtræst">Contrast</phoneme>'
        elif combined_sentences_token_list[i][0] == "contrast" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌtræst">contrast</phoneme>'

        elif combined_sentences_token_list[i][0] == "Contrast" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈtrɑːst">Contrast</phoneme>'
        elif combined_sentences_token_list[i][0] == "contrast" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈtrɑːst">contrast</phoneme>'
        elif combined_sentences_token_list[i][0] == "Contrast" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒntrɑːst">Contrast</phoneme>'
        elif combined_sentences_token_list[i][0] == "contrast" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒntrɑːst">contrast</phoneme>'
    return combined_sentences_word_list

def converse(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Converse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈvɜrs">Converse</phoneme>'
        elif combined_sentences_token_list[i][0] == "converse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈvɜrs">converse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Converse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌvɜrs">Converse</phoneme>'
        elif combined_sentences_token_list[i][0] == "converse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌvɜrs">converse</phoneme>'

        elif combined_sentences_token_list[i][0] == "Converse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈvɜːs">Converse</phoneme>'
        elif combined_sentences_token_list[i][0] == "converse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈvɜːs">converse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Converse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnvɜːs">Converse</phoneme>'
        elif combined_sentences_token_list[i][0] == "converse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnvɜːs">converse</phoneme>'
    return combined_sentences_word_list

def convert(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Convert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈvɜrt">Convert</phoneme>'
        elif combined_sentences_token_list[i][0] == "convert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈvɜrt">convert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Convert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌvɜrt">Convert</phoneme>'
        elif combined_sentences_token_list[i][0] == "convert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌvɜrt">convert</phoneme>'

        elif combined_sentences_token_list[i][0] == "Convert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈvɜːt">Convert</phoneme>'
        elif combined_sentences_token_list[i][0] == "convert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈvɜːt">convert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Convert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnvɜːt">Convert</phoneme>'
        elif combined_sentences_token_list[i][0] == "convert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnvɜːt">convert</phoneme>'
    return combined_sentences_word_list

def convict(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Convict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌvɪkt">Convict</phoneme>'
        elif combined_sentences_token_list[i][0] == "convict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɑnˌvɪkt">convict</phoneme>'
        elif combined_sentences_token_list[i][0] == "Convict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈvɪkt">Convict</phoneme>'
        elif combined_sentences_token_list[i][0] == "convict" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈvɪkt">convict</phoneme>'

        elif combined_sentences_token_list[i][0] == "Convict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnvɪkt">Convict</phoneme>'
        elif combined_sentences_token_list[i][0] == "convict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkɒnvɪkt">convict</phoneme>'
        elif combined_sentences_token_list[i][0] == "Convict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈvɪkt">Convict</phoneme>'
        elif combined_sentences_token_list[i][0] == "convict" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kənˈvɪkt">convict</phoneme>'
    return combined_sentences_word_list

def coordinate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Coordinate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="koʊˈɔrdənˌeɪt">Coordinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coordinate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="koʊˈɔrdənˌeɪt">coordinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Coordinate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="koʊˈɔrdənɪt">Coordinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coordinate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="koʊˈɔrdənɪt">coordinate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Coordinate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəʊˈɔːdɪˌneɪt">Coordinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coordinate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəʊˈɔːdɪˌneɪt">coordinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Coordinate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəʊˈɔːdɪnɪt">Coordinate</phoneme>'
        elif combined_sentences_token_list[i][0] == "coordinate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="kəʊˈɔːdɪnɪt">coordinate</phoneme>'
    return combined_sentences_word_list

#As distinct adjectives "crooked" are pronounced differently in American English, the adjectives are only included for British English
def crooked(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Crooked" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkrʊkt">Crooked</phoneme>'
        elif combined_sentences_token_list[i][0] == "crooked" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈkrʊkt">crooked</phoneme>'
        elif combined_sentences_token_list[i][0] == "Crooked" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="krʊkɪd">Crooked</phoneme>'
        elif combined_sentences_token_list[i][0] == "crooked" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="krʊkɪd">crooked</phoneme>'
    return combined_sentences_word_list

def decrease(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Decrease" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈkris">Decrease</phoneme>'
        elif combined_sentences_token_list[i][0] == "decrease" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈkris">decrease</phoneme>'
        elif combined_sentences_token_list[i][0] == "Decrease" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdiˌkris">Decrease</phoneme>'
        elif combined_sentences_token_list[i][0] == "decrease" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdiˌkris">decrease</phoneme>'

        elif combined_sentences_token_list[i][0] == "Decrease" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈkriːs">Decrease</phoneme>'
        elif combined_sentences_token_list[i][0] == "decrease" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈkriːs">decrease</phoneme>'
        elif combined_sentences_token_list[i][0] == "Decrease" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdiːkriːs">Decrease</phoneme>'
        elif combined_sentences_token_list[i][0] == "decrease" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdiːkriːs">decrease</phoneme>'
    return combined_sentences_word_list

def defect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Defect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈfɛkt">Defect</phoneme>'
        elif combined_sentences_token_list[i][0] == "defect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈfɛkt">defect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Defect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdiˌfɛkt">Defect</phoneme>'
        elif combined_sentences_token_list[i][0] == "defect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdiˌfɛkt">defect</phoneme>'

        elif combined_sentences_token_list[i][0] == "Defect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈfɛkt">Defect</phoneme>'
        elif combined_sentences_token_list[i][0] == "defect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈfɛkt">defect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Defect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdiːfɛkt">Defect</phoneme>'
        elif combined_sentences_token_list[i][0] == "defect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdiːfɛkt">defect</phoneme>'
    return combined_sentences_word_list

def degenerate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Degenerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="diˈdʒɛnərˌeɪt">Degenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "degenerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="diˈdʒɛnərˌeɪt">degenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Degenerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="diˈdʒɛnərɪt">Degenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "degenerate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="diˈdʒɛnərɪt">degenerate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Degenerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈdʒɛnəˌreɪt">Degenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "degenerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈdʒɛnəˌreɪt">degenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Degenerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈdʒɛnərɪt">Degenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "degenerate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈdʒɛnərɪt">degenerate</phoneme>'
    return combined_sentences_word_list

#Only for American English, as the noun and verb are pronounced the same in British English.
def delegate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Delegate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛləˌgeɪt">Delegate</phoneme>'
        elif combined_sentences_token_list[i][0] == "delegate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛləˌgeɪt">delegate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Delegate" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛləgɪt">Delegate</phoneme>'
        elif combined_sentences_token_list[i][0] == "delegate" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛləgɪt">delegate</phoneme>'
    return combined_sentences_word_list

def deliberate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Deliberate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈlɪbərˌeɪt">Deliberate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deliberate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈlɪbərˌeɪt">deliberate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Deliberate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈlɪbərɪt">Deliberate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deliberate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈlɪbərɪt">deliberate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Deliberate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈlɪbəˌreɪt">Deliberate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deliberate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈlɪbəˌreɪt">deliberate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Deliberate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈlɪbərɪt">Deliberate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deliberate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈlɪbərɪt">deliberate</phoneme>'
    return combined_sentences_word_list

def derogate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Derogate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈderəˌɡeit">Derogate</phoneme>'
        elif combined_sentences_token_list[i][0] == "derogate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈderəˌɡeit">derogate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Derogate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈderəɡɪt">Derogate</phoneme>'
        elif combined_sentences_token_list[i][0] == "derogate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈderəɡɪt">derogate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Derogate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛrəˌɡeɪt">Derogate</phoneme>'
        elif combined_sentences_token_list[i][0] == "derogate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛrəˌɡeɪt">derogate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Derogate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛrəɡɪt">Derogate</phoneme>'
        elif combined_sentences_token_list[i][0] == "derogate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛrəɡɪt">derogate</phoneme>'
    return combined_sentences_word_list

def desert(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Desert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈzɜrt">Desert</phoneme>'
        elif combined_sentences_token_list[i][0] == "desert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈzɜrt">desert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Desert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛzərt">Desert</phoneme>'
        elif combined_sentences_token_list[i][0] == "desert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛzərt">desert</phoneme>'

        elif combined_sentences_token_list[i][0] == "Desert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈzɜːt">Desert</phoneme>'
        elif combined_sentences_token_list[i][0] == "desert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈzɜːt">desert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Desert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛzət">Desert</phoneme>'
        elif combined_sentences_token_list[i][0] == "desert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛzət">desert</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def desolate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Desolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛsəˌleɪt">Desolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "desolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛsəˌleɪt">desolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Desolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛsəlɪt">Desolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "desolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛsəlɪt">desolate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Desolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛsəˌleɪt">Desolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "desolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛsəˌleɪt">desolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Desolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛsəlɪt">Desolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "desolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɛsəlɪt">desolate</phoneme>'
    return combined_sentences_word_list

def deviate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Deviate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdiviˌeɪt">Deviate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deviate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdiviˌeɪt">deviate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Deviate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="diviɪt">Deviate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deviate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="diviɪt">deviate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Deviate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdiːvɪˌeɪt">Deviate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deviate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdiːvɪˌeɪt">deviate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Deviate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdiːvɪɪt">Deviate</phoneme>'
        elif combined_sentences_token_list[i][0] == "deviate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdiːvɪɪt">deviate</phoneme>'
    return combined_sentences_word_list

def diagnoses(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Diagnoses" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="daɪəɡˈnəʊsiz">Diagnoses</phoneme>'
        elif combined_sentences_token_list[i][0] == "diagnoses" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="daɪəɡˈnəʊsiz">diagnoses</phoneme>'
        elif combined_sentences_token_list[i][0] == "Diagnoses" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="daɪəɡˈnəʊsəz">Diagnoses</phoneme>'
        elif combined_sentences_token_list[i][0] == "diagnoses" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="daɪəɡˈnəʊsəz">diagnoses</phoneme>'
    return combined_sentences_word_list

def diffuse(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Diffuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈfjuz">Diffuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "diffuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈfjuz">diffuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Diffuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈfjus">Diffuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "diffuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈfjus">diffuse</phoneme>'

        elif combined_sentences_token_list[i][0] == "Diffuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈfjuːz">Diffuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "diffuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈfjuːz">diffuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Diffuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈfjuːs">Diffuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "diffuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈfjuːs">diffuse</phoneme>'
    return combined_sentences_word_list

def digest(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Digest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈdʒɛst">Digest</phoneme>'
        elif combined_sentences_token_list[i][0] == "digest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈdʒɛst">digest</phoneme>'
        elif combined_sentences_token_list[i][0] == "Digest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdaɪˌdʒɛst">Digest</phoneme>'
        elif combined_sentences_token_list[i][0] == "digest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdaɪˌdʒɛst">digest</phoneme>'

        elif combined_sentences_token_list[i][0] == "Digest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈdʒɛst">Digest</phoneme>'
        elif combined_sentences_token_list[i][0] == "digest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈdʒɛst">digest</phoneme>'
        elif combined_sentences_token_list[i][0] == "Digest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈdʒɛst">Digest</phoneme>'
        elif combined_sentences_token_list[i][0] == "digest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪˈdʒɛst">digest</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def dingy(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Dingy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪŋi">Dingy</phoneme>'
        elif combined_sentences_token_list[i][0] == "dingy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪŋi">dingy</phoneme>'
        elif combined_sentences_token_list[i][0] == "Dingy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪndʒi">Dingy</phoneme>'
        elif combined_sentences_token_list[i][0] == "dingy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪndʒi">dingy</phoneme>'

        elif combined_sentences_token_list[i][0] == "Dingy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪŋɪ">Dingy</phoneme>'
        elif combined_sentences_token_list[i][0] == "dingy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪŋɪ">dingy</phoneme>'
        elif combined_sentences_token_list[i][0] == "Dingy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪndʒɪ">Dingy</phoneme>'
        elif combined_sentences_token_list[i][0] == "dingy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪndʒɪ">dingy</phoneme>'
    return combined_sentences_word_list

def discard(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Discard" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈkɑrd">Discard</phoneme>'
        elif combined_sentences_token_list[i][0] == "discard" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈkɑrd">discard</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discard" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪsˌkɑrd">Discard</phoneme>'
        elif combined_sentences_token_list[i][0] == "discard" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪsˌkɑrd">discard</phoneme>'

        elif combined_sentences_token_list[i][0] == "Discard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈkɑːd">Discard</phoneme>'
        elif combined_sentences_token_list[i][0] == "discard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈkɑːd">discard</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪskɑːd">Discard</phoneme>'
        elif combined_sentences_token_list[i][0] == "discard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪskɑːd">discard</phoneme>'
    return combined_sentences_word_list

def discharge(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Discharge" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈtʃɑrdʒ">Discharge</phoneme>'
        elif combined_sentences_token_list[i][0] == "discharge" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈtʃɑrdʒ">discharge</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discharge" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪsˌtʃɑrdʒ">Discharge</phoneme>'
        elif combined_sentences_token_list[i][0] == "discharge" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪsˌtʃɑrdʒ">discharge</phoneme>'

        elif combined_sentences_token_list[i][0] == "Discharge" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈtʃɑːdʒ">Discharge</phoneme>'
        elif combined_sentences_token_list[i][0] == "discharge" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈtʃɑːdʒ">discharge</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discharge" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪstʃɑːdʒ">Discharge</phoneme>'
        elif combined_sentences_token_list[i][0] == "discharge" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪstʃɑːdʒ">discharge</phoneme>'
    return combined_sentences_word_list

def discord(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Discord" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈkɔrd">Discord</phoneme>'
        elif combined_sentences_token_list[i][0] == "discord" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈkɔrd">discord</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discord" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪsˌkɔrd">Discord</phoneme>'
        elif combined_sentences_token_list[i][0] == "discord" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪsˌkɔrd">discord</phoneme>'

        elif combined_sentences_token_list[i][0] == "Discord" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈkɔːd">Discord</phoneme>'
        elif combined_sentences_token_list[i][0] == "discord" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈkɔːd">discord</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discord" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪskɔːd">Discord</phoneme>'
        elif combined_sentences_token_list[i][0] == "discord" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪskɔːd">discord</phoneme>'
    return combined_sentences_word_list

def discount(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Discount" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈkaʊnt">Discount</phoneme>'
        elif combined_sentences_token_list[i][0] == "discount" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈkaʊnt">discount</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discount" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪsˌkaʊnt">Discount</phoneme>'
        elif combined_sentences_token_list[i][0] == "discount" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɪsˌkaʊnt">discount</phoneme>'

        elif combined_sentences_token_list[i][0] == "Discount" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈkaʊnt">Discount</phoneme>'
        elif combined_sentences_token_list[i][0] == "discount" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈkaʊnt">discount</phoneme>'
        elif combined_sentences_token_list[i][0] == "Discount" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈkaʊnt">Discount</phoneme>'
        elif combined_sentences_token_list[i][0] == "discount" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dɪsˈkaʊnt">discount</phoneme>'
    return combined_sentences_word_list

#As the nound "do" can refer to the musical note or the short form of hairdo, only the verb was included. Also, as Spacy tokenizes "don't" as "do" and "n't",
#the phonemes are only substituted if the next element in the "combined_sentences_token_list" list isn't "n't".
def do(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Do" and English_Phonetics == "American_English" and combined_sentences_token_list[i+1][0] != "n’t" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="du">Do</phoneme>'
        elif combined_sentences_token_list[i][0] == "do" and English_Phonetics == "American_English" and combined_sentences_token_list[i+1][0] != "n’t" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="du">do</phoneme>'

        elif combined_sentences_token_list[i][0] == "Do" and English_Phonetics == "British_English" and combined_sentences_token_list[i+1][0] != "n’t" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="duː">Do</phoneme>'
        elif combined_sentences_token_list[i][0] == "do" and English_Phonetics == "British_English" and combined_sentences_token_list[i+1][0] != "n’t" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="duː">do</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately (it seems to always give the verb).
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def does(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Does" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i+1][0] != "n’t" :
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdʌzː">Does</phoneme>'
        elif combined_sentences_token_list[i][0] == "does" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i+1][0] != "n’t" :
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdʌzː">does</phoneme>'
        elif combined_sentences_token_list[i][0] == "Does" and combined_sentences_token_list[i][1][:2] == "NN" and combined_sentences_token_list[i+1][0] != "n’t":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdoʊz">Does</phoneme>'
        elif combined_sentences_token_list[i][0] == "does" and combined_sentences_token_list[i][1][:2] == "NN" and combined_sentences_token_list[i+1][0] != "n’t":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdoʊz">does</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def dogged(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Dogged" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɑgd">Dogged</phoneme>'
        elif combined_sentences_token_list[i][0] == "dogged" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɑgd">dogged</phoneme>'
        elif combined_sentences_token_list[i][0] == "Dogged" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɑgɪd">Dogged</phoneme>'
        elif combined_sentences_token_list[i][0] == "dogged" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɑgɪd">dogged</phoneme>'

        elif combined_sentences_token_list[i][0] == "Dogged" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɒɡd">Dogged</phoneme>'
        elif combined_sentences_token_list[i][0] == "dogged" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɒɡd">dogged</phoneme>'
        elif combined_sentences_token_list[i][0] == "Dogged" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɒɡɪd">Dogged</phoneme>'
        elif combined_sentences_token_list[i][0] == "dogged" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdɒɡɪd">dogged</phoneme>'
    return combined_sentences_word_list

def dove(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Dove" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="doʊv">Dove</phoneme>'
        elif combined_sentences_token_list[i][0] == "dove" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="doʊv">dove</phoneme>'
        elif combined_sentences_token_list[i][0] == "Dove" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dʌv">Dove</phoneme>'
        elif combined_sentences_token_list[i][0] == "dove" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dʌv">dove</phoneme>'

        elif combined_sentences_token_list[i][0] == "Dove" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dəʊv">Dove</phoneme>'
        elif combined_sentences_token_list[i][0] == "dove" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dəʊv">dove</phoneme>'
        elif combined_sentences_token_list[i][0] == "Dove" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dʌv">Dove</phoneme>'
        elif combined_sentences_token_list[i][0] == "dove" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="dʌv">dove</phoneme>'
    return combined_sentences_word_list

def duplicate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Duplicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈduplɪˌkeɪt">Duplicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "duplicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈduplɪˌkeɪt">duplicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Duplicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdjuplɪkɪt">Duplicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "duplicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdjuplɪkɪt">duplicate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Duplicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdjuːplɪˌkeɪt">Duplicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "duplicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdjuːplɪˌkeɪt">duplicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Duplicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdjuːplɪkɪt">Duplicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "duplicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdjuːplɪkɪt">duplicate</phoneme>'
    return combined_sentences_word_list

def egress(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Egress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈɡres">Egress</phoneme>'
        elif combined_sentences_token_list[i][0] == "egress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈɡres">egress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Egress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈiɡres">Egress</phoneme>'
        elif combined_sentences_token_list[i][0] == "egress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈiɡres">egress</phoneme>'

        elif combined_sentences_token_list[i][0] == "Egress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈɡrɛs">Egress</phoneme>'
        elif combined_sentences_token_list[i][0] == "egress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈɡrɛs">egress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Egress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈiːɡrɛs">Egress</phoneme>'
        elif combined_sentences_token_list[i][0] == "egress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈiːɡrɛs">egress</phoneme>'
    return combined_sentences_word_list

def ejaculate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Ejaculate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈdʒækjəˌleit">Ejaculate</phoneme>'
        elif combined_sentences_token_list[i][0] == "ejaculate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈdʒækjəˌleit">ejaculate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Ejaculate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈdʒækjəlɪt">Ejaculate</phoneme>'
        elif combined_sentences_token_list[i][0] == "ejaculate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈdʒækjəlɪt">ejaculate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Ejaculate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈdʒækjʊˌleɪt">Ejaculate</phoneme>'
        elif combined_sentences_token_list[i][0] == "ejaculate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈdʒækjʊˌleɪt">ejaculate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Ejaculate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈdʒækjʊlɪt">Ejaculate</phoneme>'
        elif combined_sentences_token_list[i][0] == "ejaculate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈdʒækjʊlɪt">ejaculate</phoneme>'
    return combined_sentences_word_list

def elaborate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Elaborate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈlæbəˌreɪt">Elaborate</phoneme>'
        elif combined_sentences_token_list[i][0] == "elaborate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈlæbəˌreɪt">elaborate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Elaborate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈlæbərɪt">Elaborate</phoneme>'
        elif combined_sentences_token_list[i][0] == "elaborate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈlæbərɪt">elaborate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def ellipses(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Ellipses" and combined_sentences_token_list[i][3].lower() == "ellipse":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈlɪpsɪz">Ellipses</phoneme>'
        elif combined_sentences_token_list[i][0] == "ellipses" and combined_sentences_token_list[i][3].lower() == "ellipse":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈlɪpsɪz">ellipses</phoneme>'
        elif combined_sentences_token_list[i][0] == "Ellipses" and combined_sentences_token_list[i][3].lower() == "ellipsis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈlɪpsiːz">Ellipses</phoneme>'
        elif combined_sentences_token_list[i][0] == "ellipses" and combined_sentences_token_list[i][3].lower() == "ellipsis":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈlɪpsiːz">ellipses</phoneme>'
    return combined_sentences_word_list

def entrance(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Entrance" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɛnˈtræns">Entrance</phoneme>'
        elif combined_sentences_token_list[i][0] == "entrance" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɛnˈtræns">entrance</phoneme>'
        elif combined_sentences_token_list[i][0] == "Entrance" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛntrəns">Entrance</phoneme>'
        elif combined_sentences_token_list[i][0] == "entrance" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛntrəns">entrance</phoneme>'

        elif combined_sentences_token_list[i][0] == "Entrance" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈtrɑːns">Entrance</phoneme>'
        elif combined_sentences_token_list[i][0] == "entrance" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈtrɑːns">entrance</phoneme>'
        elif combined_sentences_token_list[i][0] == "Entrance" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛntrəns">Entrance</phoneme>'
        elif combined_sentences_token_list[i][0] == "entrance" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛntrəns">entrance</phoneme>'
    return combined_sentences_word_list

def envelop(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Envelop" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="enˈveləp">Envelop</phoneme>'
        elif combined_sentences_token_list[i][0] == "envelop" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="enˈveləp">envelop</phoneme>'
        elif combined_sentences_token_list[i][0] == "Envelop" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈenvələp">Envelop</phoneme>'
        elif combined_sentences_token_list[i][0] == "envelop" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈenvələp">envelop</phoneme>'

        elif combined_sentences_token_list[i][0] == "Envelop" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈvɛləp">Envelop</phoneme>'
        elif combined_sentences_token_list[i][0] == "envelop" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈvɛləp">envelop</phoneme>'
        elif combined_sentences_token_list[i][0] == "Envelop" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛnvələp">Envelop</phoneme>'
        elif combined_sentences_token_list[i][0] == "envelop" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛnvələp">envelop</phoneme>'
    return combined_sentences_word_list

def escort(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Escort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="iˈskɔrt">Escort</phoneme>'
        elif combined_sentences_token_list[i][0] == "escort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="iˈskɔrt">escort</phoneme>'
        elif combined_sentences_token_list[i][0] == "Escort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈeskɔrt">Escort</phoneme>'
        elif combined_sentences_token_list[i][0] == "escort" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈeskɔrt">escort</phoneme>'

        elif combined_sentences_token_list[i][0] == "Escort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪsˈkɔːt">Escort</phoneme>'
        elif combined_sentences_token_list[i][0] == "escort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪsˈkɔːt">escort</phoneme>'
        elif combined_sentences_token_list[i][0] == "Escort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛskɔːt">Escort</phoneme>'
        elif combined_sentences_token_list[i][0] == "escort" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛskɔːt">escort</phoneme>'
    return combined_sentences_word_list

def essay(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Essay" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɛˈseɪ">Essay</phoneme>'
        elif combined_sentences_token_list[i][0] == "essay" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɛˈseɪ">essay</phoneme>'
        elif combined_sentences_token_list[i][0] == "Essay" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛseɪ">Essay</phoneme>'
        elif combined_sentences_token_list[i][0] == "essay" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛseɪ">essay</phoneme>'
    return combined_sentences_word_list

def estimate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Estimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛstəˌmeɪt">Estimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "estimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛstəˌmeɪt">estimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Estimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛstəmɪt">Estimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "estimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛstəmɪt">estimate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Estimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛstɪˌmeɪt">Estimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "estimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛstɪˌmeɪt">estimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Estimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛstɪmɪt">Estimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "estimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛstɪmɪt">estimate</phoneme>'
    return combined_sentences_word_list

#Only for Brisith English, as the noun and verb are pronounced the same in American English.
def excise(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Excise" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪkˈsaɪz">Excise</phoneme>'
        elif combined_sentences_token_list[i][0] == "excise" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪkˈsaɪz">excise</phoneme>'
        elif combined_sentences_token_list[i][0] == "Excise" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛksaɪz">Excise</phoneme>'
        elif combined_sentences_token_list[i][0] == "excise" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛksaɪz">excise</phoneme>'
    return combined_sentences_word_list

def excuse(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Excuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪkˈskjuz">Excuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "excuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪkˈskjuz">excuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Excuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɛkˈskjus">Excuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "excuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɛkˈskjus">excuse</phoneme>'

        elif combined_sentences_token_list[i][0] == "Excuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪkˈskjuːz">Excuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "excuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪkˈskjuːz">excuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Excuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪkˈskjuːs">Excuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "excuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪkˈskjuːs">excuse</phoneme>'
    return combined_sentences_word_list

def exploit(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Exploit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɛkˈsplɔɪt">Exploit</phoneme>'
        elif combined_sentences_token_list[i][0] == "exploit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɛkˈsplɔɪt">exploit</phoneme>'
        elif combined_sentences_token_list[i][0] == "Exploit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛksˌplɔɪt">Exploit</phoneme>'
        elif combined_sentences_token_list[i][0] == "exploit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛksˌplɔɪt">exploit</phoneme>'

        elif combined_sentences_token_list[i][0] == "Exploit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪkˈsplɔɪt">Exploit</phoneme>'
        elif combined_sentences_token_list[i][0] == "exploit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪkˈsplɔɪt">exploit</phoneme>'
        elif combined_sentences_token_list[i][0] == "Exploit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛksplɔɪt">Exploit</phoneme>'
        elif combined_sentences_token_list[i][0] == "exploit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛksplɔɪt">exploit</phoneme>'
    return combined_sentences_word_list

def extract(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Extract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪkˈstrækt">Extract</phoneme>'
        elif combined_sentences_token_list[i][0] == "extract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪkˈstrækt">extract</phoneme>'
        elif combined_sentences_token_list[i][0] == "Extract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛksˌtrækt">Extract</phoneme>'
        elif combined_sentences_token_list[i][0] == "extract" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛksˌtrækt">extract</phoneme>'

        elif combined_sentences_token_list[i][0] == "Extract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪkˈstrækt">Extract</phoneme>'
        elif combined_sentences_token_list[i][0] == "extract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪkˈstrækt">extract</phoneme>'
        elif combined_sentences_token_list[i][0] == "Extract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛkstrækt">Extract</phoneme>'
        elif combined_sentences_token_list[i][0] == "extract" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɛkstrækt">extract</phoneme>'
    return combined_sentences_word_list

def ferment(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Ferment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="fərˈmɛnt">Ferment</phoneme>'
        elif combined_sentences_token_list[i][0] == "ferment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="fərˈmɛnt">ferment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Ferment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈfɜrˌmɛnt">Ferment</phoneme>'
        elif combined_sentences_token_list[i][0] == "ferment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈfɜrˌmɛnt">ferment</phoneme>'

        elif combined_sentences_token_list[i][0] == "Ferment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="fəˈmɛnt">Ferment</phoneme>'
        elif combined_sentences_token_list[i][0] == "ferment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="fəˈmɛnt">ferment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Ferment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈfɜːmɛnt">Ferment</phoneme>'
        elif combined_sentences_token_list[i][0] == "ferment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈfɜːmɛnt">ferment</phoneme>'
    return combined_sentences_word_list

def frequent(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Frequent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="friˈkwɛnt">Frequent</phoneme>'
        elif combined_sentences_token_list[i][0] == "frequent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="friˈkwɛnt">frequent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Frequent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈfrikwənt">Frequent</phoneme>'
        elif combined_sentences_token_list[i][0] == "frequent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈfrikwənt">frequent</phoneme>'

        elif combined_sentences_token_list[i][0] == "Frequent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="frɪˈkwɛnt">Frequent</phoneme>'
        elif combined_sentences_token_list[i][0] == "frequent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="frɪˈkwɛnt">frequent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Frequent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈfriːkwənt">Frequent</phoneme>'
        elif combined_sentences_token_list[i][0] == "frequent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈfriːkwənt">frequent</phoneme>'
    return combined_sentences_word_list

def graduate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Graduate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈgrædʒuˌeɪt">Graduate</phoneme>'
        elif combined_sentences_token_list[i][0] == "graduate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈgrædʒuˌeɪt">graduate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Graduate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈgrædʒuɪt">Graduate</phoneme>'
        elif combined_sentences_token_list[i][0] == "graduate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈgrædʒuɪt">graduate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Graduate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɡrædjʊˌeɪt">Graduate</phoneme>'
        elif combined_sentences_token_list[i][0] == "graduate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɡrædjʊˌeɪt">graduate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Graduate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɡrædjʊɪt">Graduate</phoneme>'
        elif combined_sentences_token_list[i][0] == "graduate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɡrædjʊɪt">graduate</phoneme>'
    return combined_sentences_word_list

def hinder(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Hinder" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈhɪndər">Hinder</phoneme>'
        elif combined_sentences_token_list[i][0] == "hinder" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈhɪndər">hinder</phoneme>'
        elif combined_sentences_token_list[i][0] == "Hinder" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈhaɪndər">Hinder</phoneme>'
        elif combined_sentences_token_list[i][0] == "hinder" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈhaɪndər">hinder</phoneme>'

        elif combined_sentences_token_list[i][0] == "Hinder" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈhɪndə">Hinder</phoneme>'
        elif combined_sentences_token_list[i][0] == "hinder" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈhɪndə">hinder</phoneme>'
        elif combined_sentences_token_list[i][0] == "Hinder" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈhaɪndə">Hinder</phoneme>'
        elif combined_sentences_token_list[i][0] == "hinder" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈhaɪndə">hinder</phoneme>'
    return combined_sentences_word_list

def house(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "House" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="haʊz">House</phoneme>'
        elif combined_sentences_token_list[i][0] == "house" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="haʊz">house</phoneme>'
        elif combined_sentences_token_list[i][0] == "House" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="haʊs">House</phoneme>'
        elif combined_sentences_token_list[i][0] == "house" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="haʊs">house</phoneme>'
    return combined_sentences_word_list

def implant(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Implant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈplænt">Implant</phoneme>'
        elif combined_sentences_token_list[i][0] == "implant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈplænt">implant</phoneme>'
        elif combined_sentences_token_list[i][0] == "Implant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmˌplænt">Implant</phoneme>'
        elif combined_sentences_token_list[i][0] == "implant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmˌplænt">implant</phoneme>'

        elif combined_sentences_token_list[i][0] == "Implant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈplɑːnt">Implant</phoneme>'
        elif combined_sentences_token_list[i][0] == "implant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈplɑːnt">implant</phoneme>'
        elif combined_sentences_token_list[i][0] == "Implant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmˌplɑːnt">Implant</phoneme>'
        elif combined_sentences_token_list[i][0] == "implant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmˌplɑːnt">implant</phoneme>'
    return combined_sentences_word_list

def import_heteronym(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Import" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈpɔrt">Import</phoneme>'
        elif combined_sentences_token_list[i][0] == "import" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈpɔrt">import</phoneme>'
        elif combined_sentences_token_list[i][0] == "Import" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmˌpɔrt">Import</phoneme>'
        elif combined_sentences_token_list[i][0] == "import" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmˌpɔrt">import</phoneme>'

        elif combined_sentences_token_list[i][0] == "Import" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈpɔːt">Import</phoneme>'
        elif combined_sentences_token_list[i][0] == "import" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈpɔːt">import</phoneme>'
        elif combined_sentences_token_list[i][0] == "Import" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmpɔːt">Import</phoneme>'
        elif combined_sentences_token_list[i][0] == "import" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmpɔːt">import</phoneme>'
    return combined_sentences_word_list

def impress(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Impress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈprɛs">Impress</phoneme>'
        elif combined_sentences_token_list[i][0] == "impress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈprɛs">impress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Impress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmˌprɛs">Impress</phoneme>'
        elif combined_sentences_token_list[i][0] == "impress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmˌprɛs">impress</phoneme>'

        elif combined_sentences_token_list[i][0] == "Impress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈprɛs">Impress</phoneme>'
        elif combined_sentences_token_list[i][0] == "impress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈprɛs">impress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Impress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmprɛs">Impress</phoneme>'
        elif combined_sentences_token_list[i][0] == "impress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmprɛs">impress</phoneme>'
    return combined_sentences_word_list

def imprint(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Imprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈprɪnt">Imprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "imprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈprɪnt">imprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "Imprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmˌprɪnt">Imprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "imprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmˌprɪnt">imprint</phoneme>'

        elif combined_sentences_token_list[i][0] == "Imprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈprɪnt">Imprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "imprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪmˈprɪnt">imprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "Imprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmprɪnt">Imprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "imprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪmprɪnt">imprint</phoneme>'
    return combined_sentences_word_list

#As distict transitive "incense" verb forms are pronounced differently, only the noun is included.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def incense(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Incense" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌsɛns">Incense</phoneme>'
        elif combined_sentences_token_list[i][0] == "incense" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌsɛns">incense</phoneme>'

        elif combined_sentences_token_list[i][0] == "Incense" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnsɛns">Incense</phoneme>'
        elif combined_sentences_token_list[i][0] == "incense" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnsɛns">incense</phoneme>'
    return combined_sentences_word_list

def incline(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Incline" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈklaɪn">Incline</phoneme>'
        elif combined_sentences_token_list[i][0] == "incline" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈklaɪn">incline</phoneme>'
        elif combined_sentences_token_list[i][0] == "Incline" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌklaɪn">Incline</phoneme>'
        elif combined_sentences_token_list[i][0] == "incline" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌklaɪn">incline</phoneme>'

        elif combined_sentences_token_list[i][0] == "Incline" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈklaɪn">Incline</phoneme>'
        elif combined_sentences_token_list[i][0] == "incline" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈklaɪn">incline</phoneme>'
        elif combined_sentences_token_list[i][0] == "Incline" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnklaɪn">Incline</phoneme>'
        elif combined_sentences_token_list[i][0] == "incline" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnklaɪn">incline</phoneme>'
    return combined_sentences_word_list

def incorporate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Incorporate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈkɔrpəˌreɪt">Incorporate</phoneme>'
        elif combined_sentences_token_list[i][0] == "incorporate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈkɔrpəˌreɪt">incorporate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Incorporate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈkɔrpərɪt">Incorporate</phoneme>'
        elif combined_sentences_token_list[i][0] == "incorporate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈkɔrpərɪt">incorporate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Incorporate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈkɔːpəˌreɪt">Incorporate</phoneme>'
        elif combined_sentences_token_list[i][0] == "incorporate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈkɔːpəˌreɪt">incorporate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Incorporate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈkɔːpərɪt">Incorporate</phoneme>'
        elif combined_sentences_token_list[i][0] == "incorporate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈkɔːpərɪt">incorporate</phoneme>'
    return combined_sentences_word_list

def increase(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Increase" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈkris">Increase</phoneme>'
        elif combined_sentences_token_list[i][0] == "increase" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈkris">increase</phoneme>'
        elif combined_sentences_token_list[i][0] == "Increase" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnkris">Increase</phoneme>'
        elif combined_sentences_token_list[i][0] == "increase" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnkris">increase</phoneme>'

        elif combined_sentences_token_list[i][0] == "Increase" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈkriːs">Increase</phoneme>'
        elif combined_sentences_token_list[i][0] == "increase" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈkriːs">increase</phoneme>'
        elif combined_sentences_token_list[i][0] == "Increase" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnkriːs">Increase</phoneme>'
        elif combined_sentences_token_list[i][0] == "increase" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnkriːs">increase</phoneme>'
    return combined_sentences_word_list

def indent(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Indent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈdɛnt">Indent</phoneme>'
        elif combined_sentences_token_list[i][0] == "indent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈdɛnt">indent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Indent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌdɛnt">Indent</phoneme>'
        elif combined_sentences_token_list[i][0] == "indent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌdɛnt">indent</phoneme>'

        elif combined_sentences_token_list[i][0] == "Indent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈdɛnt">Indent</phoneme>'
        elif combined_sentences_token_list[i][0] == "indent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈdɛnt">indent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Indent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌdɛnt">Indent</phoneme>'
        elif combined_sentences_token_list[i][0] == "indent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌdɛnt">indent</phoneme>'
    return combined_sentences_word_list

def initiate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Initiate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈnɪʃiˌeɪt">Initiate</phoneme>'
        elif combined_sentences_token_list[i][0] == "initiate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈnɪʃiˌeɪt">initiate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Initiate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈnɪʃiɪt">Initiate</phoneme>'
        elif combined_sentences_token_list[i][0] == "initiate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈnɪʃiɪt">initiate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Initiate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈnɪʃɪˌeɪt">Initiate</phoneme>'
        elif combined_sentences_token_list[i][0] == "initiate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈnɪʃɪˌeɪt">initiate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Initiate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈnɪʃɪɪt">Initiate</phoneme>'
        elif combined_sentences_token_list[i][0] == "initiate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪˈnɪʃɪɪt">initiate</phoneme>'
    return combined_sentences_word_list

def insert(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Insert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈsɜrt">Insert</phoneme>'
        elif combined_sentences_token_list[i][0] == "insert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈsɜrt">insert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Insert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌsɜrt">Insert</phoneme>'
        elif combined_sentences_token_list[i][0] == "insert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌsɜrt">insert</phoneme>'

        elif combined_sentences_token_list[i][0] == "Insert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈsɜːt">Insert</phoneme>'
        elif combined_sentences_token_list[i][0] == "insert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈsɜːt">insert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Insert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnsɜːt">Insert</phoneme>'
        elif combined_sentences_token_list[i][0] == "insert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnsɜːt">insert</phoneme>'
    return combined_sentences_word_list

def inset(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Inset" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈsɛt">Inset</phoneme>'
        elif combined_sentences_token_list[i][0] == "inset" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈsɛt">inset</phoneme>'
        elif combined_sentences_token_list[i][0] == "Inset" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌsɛt">Inset</phoneme>'
        elif combined_sentences_token_list[i][0] == "inset" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌsɛt">inset</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def instinct(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Instinct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈstɪŋkt">Instinct</phoneme>'
        elif combined_sentences_token_list[i][0] == "instinct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈstɪŋkt">instinct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Instinct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌstɪŋkt">Instinct</phoneme>'
        elif combined_sentences_token_list[i][0] == "instinct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌstɪŋkt">instinct</phoneme>'

        elif combined_sentences_token_list[i][0] == "Instinct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈstɪŋkt">Instinct</phoneme>'
        elif combined_sentences_token_list[i][0] == "instinct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈstɪŋkt">instinct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Instinct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnstɪŋkt">Instinct</phoneme>'
        elif combined_sentences_token_list[i][0] == "instinct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnstɪŋkt">instinct</phoneme>'
    return combined_sentences_word_list

def insult(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Insult" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈsʌlt">Insult</phoneme>'
        elif combined_sentences_token_list[i][0] == "insult" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈsʌlt">insult</phoneme>'
        elif combined_sentences_token_list[i][0] == "Insult" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌsʌlt">Insult</phoneme>'
        elif combined_sentences_token_list[i][0] == "insult" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌsʌlt">insult</phoneme>'

        elif combined_sentences_token_list[i][0] == "Insult" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈsʌlt">Insult</phoneme>'
        elif combined_sentences_token_list[i][0] == "insult" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈsʌlt">insult</phoneme>'
        elif combined_sentences_token_list[i][0] == "Insult" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnsʌlt">Insult</phoneme>'
        elif combined_sentences_token_list[i][0] == "insult" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnsʌlt">insult</phoneme>'
    return combined_sentences_word_list

def intercept(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Intercept" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌɪntərˈsɛpt">Intercept</phoneme>'
        elif combined_sentences_token_list[i][0] == "intercept" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌɪntərˈsɛpt">intercept</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intercept" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntərˌsɛpt">Intercept</phoneme>'
        elif combined_sentences_token_list[i][0] == "intercept" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntərˌsɛpt">intercept</phoneme>'

        elif combined_sentences_token_list[i][0] == "Intercept" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌɪntəˈsɛpt">Intercept</phoneme>'
        elif combined_sentences_token_list[i][0] == "intercept" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌɪntəˈsɛpt">intercept</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intercept" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntəˌsɛpt">Intercept</phoneme>'
        elif combined_sentences_token_list[i][0] == "intercept" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntəˌsɛpt">intercept</phoneme>'
    return combined_sentences_word_list

def intermediate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Intermediate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌɪntərˈmidiˌeɪt">Intermediate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intermediate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌɪntərˈmidiˌeɪt">intermediate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intermediate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌɪntərˈmidiɪt">Intermediate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intermediate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌɪntərˈmidiɪt">intermediate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Intermediate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌɪntəˈmiːdɪˌeɪt">Intermediate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intermediate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌɪntəˈmiːdɪˌeɪt">intermediate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intermediate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌɪntəˈmiːdɪɪt">Intermediate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intermediate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌɪntəˈmiːdɪɪt">intermediate</phoneme>'
    return combined_sentences_word_list

#As the transitive and intransitive versions of the verb "intern" are pronounced differently, a function is used to determine whether
#the verb is transitive or not. However, Spacy does not yet allow to accurately distinguish between transitive and intransitive verbs.
#If the verb "intern" is labelled as a transitive verb by Spacy (To detain or to confine people or material during a conflict, for instance),
#it is replaced by the phoneme "<phoneme alphabet="ipa" ph="ɪnˈtɜrn">Intern</phoneme>". #If the verb "intern" is labelled as an intransitive verb by Spacy (to be employed as an intern), it is replaced with the phoneme
#"<phoneme alphabet="ipa" ph="ˈɪnˌtɜrn">Intern</phoneme>"
def intern(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Intern" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            if is_transitive_verb(combined_sentences_token_list) == True:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈtɜrn">Intern</phoneme>'
            else:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌtɜrn">Intern</phoneme>'
        elif combined_sentences_token_list[i][0] == "intern" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            if is_transitive_verb(combined_sentences_token_list) == True:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈtɜrn">Intern</phoneme>'
            else:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌtɜrn">Intern</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intern" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌtɜrn">Intern</phoneme>'
        elif combined_sentences_token_list[i][0] == "intern" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌtɜrn">intern</phoneme>'

        elif combined_sentences_token_list[i][0] == "Intern" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            if is_transitive_verb(combined_sentences_token_list) == True:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈtɜːn">Intern</phoneme>'
            else:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntɜːn">Intern</phoneme>'
        elif combined_sentences_token_list[i][0] == "intern" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            if is_transitive_verb(combined_sentences_token_list) == True:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈtɜːn">Intern</phoneme>'
            else:
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntɜːn">Intern</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intern" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntɜːn">Intern</phoneme>'
        elif combined_sentences_token_list[i][0] == "intern" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntɜːn">intern</phoneme>'
    return combined_sentences_word_list

def intimate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Intimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntəˌmeɪt">Intimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntəˌmeɪt">intimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntəmət">Intimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntəmət">intimate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Intimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntɪˌmeɪt">Intimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntɪˌmeɪt">intimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Intimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntɪmɪt">Intimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "intimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪntɪmɪt">intimate</phoneme>'
    return combined_sentences_word_list

def invite(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Invite" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈvaɪt">Invite</phoneme>'
        elif combined_sentences_token_list[i][0] == "invite" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈvaɪt">invite</phoneme>'
        elif combined_sentences_token_list[i][0] == "Invite" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌvaɪt">Invite</phoneme>'
        elif combined_sentences_token_list[i][0] == "invite" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnˌvaɪt">invite</phoneme>'

        elif combined_sentences_token_list[i][0] == "Invite" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈvaɪt">Invite</phoneme>'
        elif combined_sentences_token_list[i][0] == "invite" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɪnˈvaɪt">invite</phoneme>'
        elif combined_sentences_token_list[i][0] == "Invite" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnvaɪt">Invite</phoneme>'
        elif combined_sentences_token_list[i][0] == "invite" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnvaɪt">invite</phoneme>'
    return combined_sentences_word_list

#Only for British English, as the noun, verb and adjective may be pronounced the same in American English
def involute(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Involute" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌɪnvəˈluːt">Involute</phoneme>'
        elif combined_sentences_token_list[i][0] == "involute" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌɪnvəˈluːt">involute</phoneme>'
        elif combined_sentences_token_list[i][0] == "Involute" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnvəˌluːt">Involute</phoneme>'
        elif combined_sentences_token_list[i][0] == "involute" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɪnvəˌluːt">involute</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def isolate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Isolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈaisəˌleit">Isolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "isolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈaisəˌleit">isolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Isolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈaisəlɪt">Isolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "isolate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈaisəlɪt">isolate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Isolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈaɪsəˌleɪt">Isolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "isolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈaɪsəˌleɪt">isolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Isolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈaɪsəlɪt">Isolate</phoneme>'
        elif combined_sentences_token_list[i][0] == "isolate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈaɪsəlɪt">isolate</phoneme>'
    return combined_sentences_word_list

def jagged(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Jagged" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdʒægd">Jagged</phoneme>'
        elif combined_sentences_token_list[i][0] == "jagged" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdʒægd">jagged</phoneme>'
        elif combined_sentences_token_list[i][0] == "Jagged" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdʒægɪd">Jagged</phoneme>'
        elif combined_sentences_token_list[i][0] == "jagged" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈdʒægɪd">jagged</phoneme>'
    return combined_sentences_word_list

#As the noun "lead" can designate the chemical element or the first place, and as some transitive "lead" verbs forms
#are pronounced differently, only the intransitive verb and adjective are included.
def lead(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Lead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == False:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lid">Lead</phoneme>'
        elif combined_sentences_token_list[i][0] == "lead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == False:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lid">lead</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lid">Lead</phoneme>'
        elif combined_sentences_token_list[i][0] == "lead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lid">lead</phoneme>'

        elif combined_sentences_token_list[i][0] == "Lead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == False:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="liːd">Lead</phoneme>'
        elif combined_sentences_token_list[i][0] == "lead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == False:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="liːd">lead</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="liːd">Lead</phoneme>'
        elif combined_sentences_token_list[i][0] == "lead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="liːd">lead</phoneme>'
    return combined_sentences_word_list

#As some "learned" adjective forms are pronounced differently in American English, the adjective is
#only covered in British English, where all adjective forms are pronounced the same.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def learned(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Learned" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈlɜːrnd">Learned</phoneme>'
        elif combined_sentences_token_list[i][0] == "learned" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈlɜːrnd">learned</phoneme>'
        elif combined_sentences_token_list[i][0] == "Learned" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈlɜːnɪd">Learned</phoneme>'
        elif combined_sentences_token_list[i][0] == "learned" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈlɜːnɪd">learned</phoneme>'
    return combined_sentences_word_list

def legitimate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Legitimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ləˈdʒɪtəˌmeɪt">Legitimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "legitimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ləˈdʒɪtəˌmeɪt">legitimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Legitimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ləˈdʒɪtəmət">Legitimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "legitimate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ləˈdʒɪtəmət">legitimate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Legitimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lɪˈdʒɪtɪˌmeɪt">Legitimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "legitimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lɪˈdʒɪtɪˌmeɪt">legitimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Legitimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lɪˈdʒɪtɪmɪt">Legitimate</phoneme>'
        elif combined_sentences_token_list[i][0] == "legitimate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lɪˈdʒɪtɪmɪt">legitimate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def lied(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Lied" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="laid">Lied</phoneme>'
        elif combined_sentences_token_list[i][0] == "lied" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="laid">lied</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lied" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lid">Lied</phoneme>'
        elif combined_sentences_token_list[i][0] == "lied" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lid">lied</phoneme>'

        elif combined_sentences_token_list[i][0] == "Lied" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="laid">Lied</phoneme>'
        elif combined_sentences_token_list[i][0] == "lied" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="laid">lied</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lied" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="liːd">Lied</phoneme>'
        elif combined_sentences_token_list[i][0] == "lied" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="liːd">lied</phoneme>'
    return combined_sentences_word_list

def live(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Live" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lɪv">Live</phoneme>'
        elif combined_sentences_token_list[i][0] == "live" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="lɪv">live</phoneme>'
        elif combined_sentences_token_list[i][0] == "Live" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="laɪv">Live</phoneme>'
        elif combined_sentences_token_list[i][0] == "live" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="laɪv">live</phoneme>'
    return combined_sentences_word_list

#As different forms of the noun and intransitive verb "lower" can be pronounced in different ways, only the adjectives and transitive verbs are included.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def lower(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Lower" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == True:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈloʊər">Lower</phoneme>'
        elif combined_sentences_token_list[i][0] == "lower" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == True:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈloʊər">lower</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lower" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈloʊər">Lower</phoneme>'
        elif combined_sentences_token_list[i][0] == "lower" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈloʊər">lower</phoneme>'

        elif combined_sentences_token_list[i][0] == "Lower" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == True:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈləʊə">Lower</phoneme>'
        elif combined_sentences_token_list[i][0] == "lower" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB" and is_transitive_verb(combined_sentences_token_list) == True:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈləʊə">lower</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lower" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈləʊə">Lower</phoneme>'
        elif combined_sentences_token_list[i][0] == "lower" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈləʊə">lower</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def lupine(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Lupine" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈluˌpaɪn">Lupine</phoneme>'
        elif combined_sentences_token_list[i][0] == "lupine" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈluˌpaɪn">lupine</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lupine" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈlupɪn">Lupine</phoneme>'
        elif combined_sentences_token_list[i][0] == "lupine" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈlupɪn">lupine</phoneme>'

        elif combined_sentences_token_list[i][0] == "Lupine" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈluːpaɪn">Lupine</phoneme>'
        elif combined_sentences_token_list[i][0] == "lupine" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈluːpaɪn">lupine</phoneme>'
        elif combined_sentences_token_list[i][0] == "Lupine" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈlupɪn">Lupine</phoneme>'
        elif combined_sentences_token_list[i][0] == "lupine" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈlupɪn">lupine</phoneme>'
    return combined_sentences_word_list

def merchandise(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Merchandise" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɜrtʃənˌdaɪz">Merchandise</phoneme>'
        elif combined_sentences_token_list[i][0] == "merchandise" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɜrtʃənˌdaɪz">merchandise</phoneme>'
        elif combined_sentences_token_list[i][0] == "Merchandise" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɜrtʃənˌdaɪs">Merchandise</phoneme>'
        elif combined_sentences_token_list[i][0] == "merchandise" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɜrtʃənˌdaɪs">merchandise</phoneme>'

        elif combined_sentences_token_list[i][0] == "Merchandise" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɜːtʃənˌdaɪz">Merchandise</phoneme>'
        elif combined_sentences_token_list[i][0] == "merchandise" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɜːtʃənˌdaɪz">merchandise</phoneme>'
        elif combined_sentences_token_list[i][0] == "Merchandise" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɜːtʃənˌdaɪs">Merchandise</phoneme>'
        elif combined_sentences_token_list[i][0] == "merchandise" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɜːtʃənˌdaɪs">merchandise</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def minute(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Minute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="maɪˈnjut">Minute</phoneme>'
        elif combined_sentences_token_list[i][0] == "minute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="maɪˈnjut">minute</phoneme>'
        elif combined_sentences_token_list[i][0] == "Minute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɪnɪt">Minute</phoneme>'
        elif combined_sentences_token_list[i][0] == "minute" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɪnɪt">minute</phoneme>'

        elif combined_sentences_token_list[i][0] == "Minute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="maɪˈnjuːt">Minute</phoneme>'
        elif combined_sentences_token_list[i][0] == "minute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="maɪˈnjuːt">minute</phoneme>'
        elif combined_sentences_token_list[i][0] == "Minute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɪnɪt">Minute</phoneme>'
        elif combined_sentences_token_list[i][0] == "minute" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɪnɪt">minute</phoneme>'
    return combined_sentences_word_list

def misconduct(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Misconduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌmɪskənˈdʌkt">Misconduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "misconduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌmɪskənˈdʌkt">misconduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Misconduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="mɪsˈkɑndʌkt">Misconduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "misconduct" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="mɪsˈkɑndʌkt">misconduct</phoneme>'

        elif combined_sentences_token_list[i][0] == "Misconduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌmɪskənˈdʌkt">Misconduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "misconduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌmɪskənˈdʌkt">misconduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "Misconduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="mɪsˈkɒndʌkt">Misconduct</phoneme>'
        elif combined_sentences_token_list[i][0] == "misconduct" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="mɪsˈkɒndʌkt">misconduct</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def misread(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Misread" and combined_sentences_token_list[i][1] in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌmɪsˈriːd">Misread</phoneme>'
        elif combined_sentences_token_list[i][0] == "misread" and combined_sentences_token_list[i][1] in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌmɪsˈriːd">misread</phoneme>'
        elif combined_sentences_token_list[i][0] == "Misread" and combined_sentences_token_list[i][1] not in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌmɪsˈrɛd">Misread</phoneme>'
        elif combined_sentences_token_list[i][0] == "misread" and combined_sentences_token_list[i][1] not in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌmɪsˈrɛd">misread</phoneme>'
    return combined_sentences_word_list

#As the two noun forms of "mobile" ("mobile" as in cell phone, "mobile" as in an abstract sculpture) are pronounced differently in American English, only the
#adjectives and the proper noun are included (the regular nouns are included in British English).
def mobile(combined_sentences_word_list, combined_sentences_token_list):
    global English_Phonetics
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Mobile" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:3] == "NNP":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmoʊˌbil">Mobile</phoneme>'
        elif combined_sentences_token_list[i][0] == "Mobile" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmoʊˌbaɪl">Mobile</phoneme>'
        elif combined_sentences_token_list[i][0] == "mobile" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmoʊˌbaɪl">mobile</phoneme>'

        elif combined_sentences_token_list[i][0] == "Mobile" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:3] == "NNP":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈməʊbiːl">Mobile</phoneme>'
        elif combined_sentences_token_list[i][0] == "Mobile" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈməʊbaɪl">Mobile</phoneme>'
        elif combined_sentences_token_list[i][0] == "mobile" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈməʊbaɪl">mobile</phoneme>'
        elif combined_sentences_token_list[i][0] == "Mobile" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈməʊbaɪl">Mobile</phoneme>'
        elif combined_sentences_token_list[i][0] == "mobile" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈməʊbaɪl">mobile</phoneme>'
    return combined_sentences_word_list

def moderate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Moderate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɑdərˌeɪt">Moderate</phoneme>'
        elif combined_sentences_token_list[i][0] == "moderate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɑdərˌeɪt">moderate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Moderate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɑdərɪt">Moderate</phoneme>'
        elif combined_sentences_token_list[i][0] == "moderate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɑdərɪt">moderate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Moderate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɒdəˌreɪt">Moderate</phoneme>'
        elif combined_sentences_token_list[i][0] == "moderate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɒdəˌreɪt">moderate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Moderate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɒdərɪt">Moderate</phoneme>'
        elif combined_sentences_token_list[i][0] == "moderate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmɒdərɪt">moderate</phoneme>'
    return combined_sentences_word_list

def moped(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Moped" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmoʊpt">Moped</phoneme>'
        elif combined_sentences_token_list[i][0] == "moped" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmoʊpt">moped</phoneme>'
        elif combined_sentences_token_list[i][0] == "Moped" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmoʊˌpɛd">Moped</phoneme>'
        elif combined_sentences_token_list[i][0] == "moped" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmoʊˌpɛd">moped</phoneme>'

        elif combined_sentences_token_list[i][0] == "Moped" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmoʊpd">Moped</phoneme>'
        elif combined_sentences_token_list[i][0] == "moped" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmoʊpd">moped</phoneme>'
        elif combined_sentences_token_list[i][0] == "Moped" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈməʊpɛd">Moped</phoneme>'
        elif combined_sentences_token_list[i][0] == "moped" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈməʊpɛd">moped</phoneme>'
    return combined_sentences_word_list

def mouse(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Mouse" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="maʊz">Mouse</phoneme>'
        elif combined_sentences_token_list[i][0] == "mouse" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="maʊz">mouse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Mouse" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="maʊs">Mouse</phoneme>'
        elif combined_sentences_token_list[i][0] == "mouse" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="maʊs">mouse</phoneme>'
    return combined_sentences_word_list

def mouth(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Mouth" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="maʊð">Mouth</phoneme>'
        elif combined_sentences_token_list[i][0] == "mouth" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="maʊð">mouth</phoneme>'
        elif combined_sentences_token_list[i][0] == "Mouth" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="maʊθ">Mouth</phoneme>'
        elif combined_sentences_token_list[i][0] == "mouth" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="maʊθ">mouth</phoneme>'
    return combined_sentences_word_list

def mow(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Mow" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmoʊ">Mow</phoneme>'
        elif combined_sentences_token_list[i][0] == "mow" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmoʊ">mow</phoneme>'
        elif combined_sentences_token_list[i][0] == "Mow" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmaʊ">Mow</phoneme>'
        elif combined_sentences_token_list[i][0] == "mow" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmaʊ">mow</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately. (It seems to tokenize multiply as either a verb
#or comparative adjective (instead of adverb)) The POS was used instead of the TAG for the adverbs, as the first
#letters of the various adverb tags differ.
def multiply(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Multiply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmʌltəˌplaɪ">Multiply</phoneme>'
        elif combined_sentences_token_list[i][0] == "multiply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmʌltəˌplaɪ">multiply</phoneme>'
        elif combined_sentences_token_list[i][0] == "Multiply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmʌltəpli">Multiply</phoneme>'
        elif combined_sentences_token_list[i][0] == "multiply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmʌltəpli">multiply</phoneme>'

        elif combined_sentences_token_list[i][0] == "Multiply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmʌltɪˌplaɪ">Multiply</phoneme>'
        elif combined_sentences_token_list[i][0] == "multiply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmʌltɪˌplaɪ">multiply</phoneme>'
        elif combined_sentences_token_list[i][0] == "Multiply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmʌltɪpli">Multiply</phoneme>'
        elif combined_sentences_token_list[i][0] == "multiply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈmʌltɪpli">multiply</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def number(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Number" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈnʌmər">Number</phoneme>'
        elif combined_sentences_token_list[i][0] == "number" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈnʌmər">number</phoneme>'
        elif combined_sentences_token_list[i][0] == "Number" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈnʌmbər">Number</phoneme>'
        elif combined_sentences_token_list[i][0] == "number" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈnʌmbər">number</phoneme>'

        elif combined_sentences_token_list[i][0] == "Number" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈnʌmə">Number</phoneme>'
        elif combined_sentences_token_list[i][0] == "number" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈnʌmə">number</phoneme>'
        elif combined_sentences_token_list[i][0] == "Number" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈnʌmbə">Number</phoneme>'
        elif combined_sentences_token_list[i][0] == "number" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈnʌmbə">number</phoneme>'
    return combined_sentences_word_list

def object(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Object" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əbˈdʒɛkt">Object</phoneme>'
        elif combined_sentences_token_list[i][0] == "object" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əbˈdʒɛkt">object</phoneme>'
        elif combined_sentences_token_list[i][0] == "Object" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɑbdʒɛkt">Object</phoneme>'
        elif combined_sentences_token_list[i][0] == "object" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ɑbdʒɛkt">object</phoneme>'

        elif combined_sentences_token_list[i][0] == "Object" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əbˈdʒɛkt">Object</phoneme>'
        elif combined_sentences_token_list[i][0] == "object" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="əbˈdʒɛkt">object</phoneme>'
        elif combined_sentences_token_list[i][0] == "Object" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɒbdʒɪkt">Object</phoneme>'
        elif combined_sentences_token_list[i][0] == "object" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɒbdʒɪkt">object</phoneme>'
    return combined_sentences_word_list

#Only in American English, as it is pronounced the same in British English.
def obligate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Obligate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɑblɪˌgeɪt">Obligate</phoneme>'
        elif combined_sentences_token_list[i][0] == "obligate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɑblɪˌgeɪt">obligate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Obligate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɑbləgɪt">Obligate</phoneme>'
        elif combined_sentences_token_list[i][0] == "obligate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈɑbləgɪt">obligate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def overage(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Overage" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌoʊvərˈeɪdʒ">Overage</phoneme>'
        elif combined_sentences_token_list[i][0] == "overage" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌoʊvərˈeɪdʒ">overage</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overage" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈoʊvərɪdʒ">Overage</phoneme>'
        elif combined_sentences_token_list[i][0] == "overage" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈoʊvərɪdʒ">overage</phoneme>'

        elif combined_sentences_token_list[i][0] == "Overage" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌəʊvərˈeɪdʒ">Overage</phoneme>'
        elif combined_sentences_token_list[i][0] == "overage" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌəʊvərˈeɪdʒ">overage</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overage" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈəʊvərɪdʒ">Overage</phoneme>'
        elif combined_sentences_token_list[i][0] == "overage" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈəʊvərɪdʒ">overage</phoneme>'
    return combined_sentences_word_list

#The POS was used instead of the TAG for the adverbs, as the first letters of the various adverb tags differ.
def overall(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Overall" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈoʊvərˌɔl">Overall</phoneme>'
        elif combined_sentences_token_list[i][0] == "overall" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈoʊvərˌɔl">overall</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overall" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="oʊvərˈɔl">Overall</phoneme>'
        elif combined_sentences_token_list[i][0] == "overall" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="oʊvərˈɔl">overall</phoneme>'

        elif combined_sentences_token_list[i][0] == "Overall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈəʊvərˌɔːl">Overall</phoneme>'
        elif combined_sentences_token_list[i][0] == "overall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈəʊvərˌɔːl">overall</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌəʊvərˈɔːl">Overall</phoneme>'
        elif combined_sentences_token_list[i][0] == "overall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌəʊvərˈɔːl">overall</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
#The POS was used instead of the TAG for the adverbs, as the first letters of the various adverb tags differ.
def overhead(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Overhead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈoʊvərˌhɛd">Overhead</phoneme>'
        elif combined_sentences_token_list[i][0] == "overhead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈoʊvərˌhɛd">overhead</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overhead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="oʊvərˈhɛd">Overhead</phoneme>'
        elif combined_sentences_token_list[i][0] == "overhead" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="oʊvərˈhɛd">overhead</phoneme>'

        elif combined_sentences_token_list[i][0] == "Overhead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈəʊvəˌhɛd">Overhead</phoneme>'
        elif combined_sentences_token_list[i][0] == "overhead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈəʊvəˌhɛd">overhead</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overhead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌəʊvəˈhɛd">Overhead</phoneme>'
        elif combined_sentences_token_list[i][0] == "overhead" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌəʊvəˈhɛd">overhead</phoneme>'
    return combined_sentences_word_list

def overlook(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Overlook" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌoʊvərˈlʊk">Overlook</phoneme>'
        elif combined_sentences_token_list[i][0] == "overlook" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌoʊvərˈlʊk">overlook</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overlook" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈoʊvərˌlʊk">Overlook</phoneme>'
        elif combined_sentences_token_list[i][0] == "overlook" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈoʊvərˌlʊk">overlook</phoneme>'

        elif combined_sentences_token_list[i][0] == "Overlook" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌəʊvəˈlʊk">Overlook</phoneme>'
        elif combined_sentences_token_list[i][0] == "overlook" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌəʊvəˈlʊk">overlook</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overlook" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈəʊvəˌlʊk">Overlook</phoneme>'
        elif combined_sentences_token_list[i][0] == "overlook" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈəʊvəˌlʊk">overlook</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def overrun(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Overrun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌoʊvərˈrʌn">Overrun</phoneme>'
        elif combined_sentences_token_list[i][0] == "overrun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌoʊvərˈrʌn">overrun</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overrun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈoʊvərˌrʌn">Overrun</phoneme>'
        elif combined_sentences_token_list[i][0] == "overrun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈoʊvərˌrʌn">overrun</phoneme>'

        elif combined_sentences_token_list[i][0] == "Overrun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌəʊvəˈrʌn">Overrun</phoneme>'
        elif combined_sentences_token_list[i][0] == "overrun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌəʊvəˈrʌn">overrun</phoneme>'
        elif combined_sentences_token_list[i][0] == "Overrun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈəʊvəˌrʌn">Overrun</phoneme>'
        elif combined_sentences_token_list[i][0] == "overrun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈəʊvəˌrʌn">overrun</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def pedal(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Pedal" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpedl">Pedal</phoneme>'
        elif combined_sentences_token_list[i][0] == "pedal" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpedl">pedal</phoneme>'
        elif combined_sentences_token_list[i][0] == "Pedal" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpidl">Pedal</phoneme>'
        elif combined_sentences_token_list[i][0] == "pedal" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpidl">pedal</phoneme>'

        elif combined_sentences_token_list[i][0] == "Pedal" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɛdəl">Pedal</phoneme>'
        elif combined_sentences_token_list[i][0] == "pedal" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "VB"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɛdəl">pedal</phoneme>'
        elif combined_sentences_token_list[i][0] == "Pedal" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpiːdəl">Pedal</phoneme>'
        elif combined_sentences_token_list[i][0] == "pedal" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpiːdəl">pedal</phoneme>'
    return combined_sentences_word_list

def perfect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Perfect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pərˈfɛkt">Perfect</phoneme>'
        elif combined_sentences_token_list[i][0] == "perfect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pərˈfɛkt">perfect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Perfect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɜrfɪkt">Perfect</phoneme>'
        elif combined_sentences_token_list[i][0] == "perfect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɜrfɪkt">perfect</phoneme>'

        elif combined_sentences_token_list[i][0] == "Perfect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pəˈfɛkt">Perfect</phoneme>'
        elif combined_sentences_token_list[i][0] == "perfect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pəˈfɛkt">perfect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Perfect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɜːfɪkt">Perfect</phoneme>'
        elif combined_sentences_token_list[i][0] == "perfect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɜːfɪkt">perfect</phoneme>'
    return combined_sentences_word_list

def permit(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Permit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pərˈmɪt">Permit</phoneme>'
        elif combined_sentences_token_list[i][0] == "permit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pərˈmɪt">permit</phoneme>'
        elif combined_sentences_token_list[i][0] == "Permit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɜrˌmɪt">Permit</phoneme>'
        elif combined_sentences_token_list[i][0] == "permit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɜrˌmɪt">permit</phoneme>'

        elif combined_sentences_token_list[i][0] == "Permit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pəˈmɪt">Permit</phoneme>'
        elif combined_sentences_token_list[i][0] == "permit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pəˈmɪt">permit</phoneme>'
        elif combined_sentences_token_list[i][0] == "Permit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɜːmɪt">Permit</phoneme>'
        elif combined_sentences_token_list[i][0] == "permit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɜːmɪt">permit</phoneme>'
    return combined_sentences_word_list

def pervert(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Pervert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pərˈvɜrt">Pervert</phoneme>'
        elif combined_sentences_token_list[i][0] == "pervert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pərˈvɜrt">pervert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Pervert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɜrˌvɜrt">Pervert</phoneme>'
        elif combined_sentences_token_list[i][0] == "pervert" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɜrˌvɜrt">pervert</phoneme>'

        elif combined_sentences_token_list[i][0] == "Pervert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pəˈvɜːt">Pervert</phoneme>'
        elif combined_sentences_token_list[i][0] == "pervert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="pəˈvɜːt">pervert</phoneme>'
        elif combined_sentences_token_list[i][0] == "Pervert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɜːvɜːt">Pervert</phoneme>'
        elif combined_sentences_token_list[i][0] == "pervert" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɜːvɜːt">pervert</phoneme>'
    return combined_sentences_word_list

def polish(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Polish" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1] == "NNP":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpoulɪʃ">Polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "Polish" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɑlɪʃ">Polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "polish" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɑlɪʃ">polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "Polish" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpoulɪʃ">Polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "polish" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpoulɪʃ">polish</phoneme>'

        elif combined_sentences_token_list[i][0] == "Polish" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1] == "NNP":
                combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpəʊlɪʃ">Polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "Polish" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɒlɪʃ">Polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "polish" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɒlɪʃ">polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "Polish" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpəʊlɪʃ">Polish</phoneme>'
        elif combined_sentences_token_list[i][0] == "polish" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpəʊlɪʃ">polish</phoneme>'
    return combined_sentences_word_list

def postulate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Postulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɑstʃəˌleɪt">Postulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "postulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɑstʃəˌleɪt">postulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Postulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɑstʃəlɪt">Postulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "postulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɑstʃəlɪt">postulate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Postulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɒstjʊˌleɪt">Postulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "postulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɒstjʊˌleɪt">postulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Postulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɒstjʊlɪt">Postulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "postulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpɒstjʊlɪt">postulate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def precedent(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Precedent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prɪˈsiːdənt">Precedent</phoneme>'
        elif combined_sentences_token_list[i][0] == "precedent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prɪˈsiːdənt">precedent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Precedent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɛsɪdənt">Precedent</phoneme>'
        elif combined_sentences_token_list[i][0] == "precedent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɛsɪdənt">precedent</phoneme>'

        elif combined_sentences_token_list[i][0] == "Precedent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="priˈsidənt">Precedent</phoneme>'
        elif combined_sentences_token_list[i][0] == "precedent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="priˈsidənt">precedent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Precedent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɛsɪdənt">Precedent</phoneme>'
        elif combined_sentences_token_list[i][0] == "precedent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɛsɪdənt">precedent</phoneme>'
    return combined_sentences_word_list

def precipitate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Precipitate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="priˈsɪpəˌteɪt">Precipitate</phoneme>'
        elif combined_sentences_token_list[i][0] == "precipitate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="priˈsɪpəˌteɪt">precipitate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Precipitate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="priˈsɪpətɪt">Precipitate</phoneme>'
        elif combined_sentences_token_list[i][0] == "precipitate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="priˈsɪpətɪt">precipitate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Precipitate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prɪˈsɪpɪˌteɪt">Precipitate</phoneme>'
        elif combined_sentences_token_list[i][0] == "precipitate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prɪˈsɪpɪˌteɪt">precipitate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Precipitate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prɪˈsɪpɪtɪt">Precipitate</phoneme>'
        elif combined_sentences_token_list[i][0] == "precipitate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prɪˈsɪpɪtɪt">precipitate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def predicate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Predicate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɛdɪˌkeɪt">Predicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "predicate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɛdɪˌkeɪt">predicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Predicate" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɛdɪkɪt">Predicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "predicate" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɛdɪkɪt">predicate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def premise(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Premise" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prɪˈmaɪz">Premise</phoneme>'
        elif combined_sentences_token_list[i][0] == "premise" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prɪˈmaɪz">premise</phoneme>'
        elif combined_sentences_token_list[i][0] == "Premise" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɛmɪs">Premise</phoneme>'
        elif combined_sentences_token_list[i][0] == "premise" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɛmɪs">premise</phoneme>'
    return combined_sentences_word_list

def present(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Present" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prɪˈzɛnt">Present</phoneme>'
        elif combined_sentences_token_list[i][0] == "present" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prɪˈzɛnt">present</phoneme>'
        elif combined_sentences_token_list[i][0] == "Present" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɛzənt">Present</phoneme>'
        elif combined_sentences_token_list[i][0] == "present" and combined_sentences_token_list[i][1][:2] in ["JJ", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɛzənt">present</phoneme>'
    return combined_sentences_word_list

def proceeds(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Proceeds" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prəˈsiːdz">Proceeds</phoneme>'
        elif combined_sentences_token_list[i][0] == "proceeds" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prəˈsiːdz">proceeds</phoneme>'
        elif combined_sentences_token_list[i][0] == "Proceeds" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈproʊsiːdz">Proceeds</phoneme>'
        elif combined_sentences_token_list[i][0] == "proceeds" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈproʊsiːdz">proceeds</phoneme>'
    return combined_sentences_word_list

def produce(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Produce" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prəˈduːs">Produce</phoneme>'
        elif combined_sentences_token_list[i][0] == "produce" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prəˈduːs">produce</phoneme>'
        elif combined_sentences_token_list[i][0] == "Produce" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɑduːs">Produce</phoneme>'
        elif combined_sentences_token_list[i][0] == "produce" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɑduːs">produce</phoneme>'

        elif combined_sentences_token_list[i][0] == "Produce" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="proʊˈdus">Produce</phoneme>'
        elif combined_sentences_token_list[i][0] == "produce" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="proʊˈdus">produce</phoneme>'
        elif combined_sentences_token_list[i][0] == "Produce" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈproʊˌdus">Produce</phoneme>'
        elif combined_sentences_token_list[i][0] == "produce" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈproʊˌdus">produce</phoneme>'
    return combined_sentences_word_list

def progress(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Progress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="proʊˈgrɛs">Progress</phoneme>'
        elif combined_sentences_token_list[i][0] == "progress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="proʊˈgrɛs">progress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Progress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɑgrɛs">Progress</phoneme>'
        elif combined_sentences_token_list[i][0] == "progress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɑgrɛs">progress</phoneme>'

        elif combined_sentences_token_list[i][0] == "Progress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prəˈɡrɛs">Progress</phoneme>'
        elif combined_sentences_token_list[i][0] == "progress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prəˈɡrɛs">progress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Progress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprəʊɡrɛs">Progress</phoneme>'
        elif combined_sentences_token_list[i][0] == "progress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprəʊɡrɛs">progress</phoneme>'
    return combined_sentences_word_list

def project(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Project" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prəˈdʒɛkt">Project</phoneme>'
        elif combined_sentences_token_list[i][0] == "project" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prəˈdʒɛkt">project</phoneme>'
        elif combined_sentences_token_list[i][0] == "Project" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɑˌdʒɛkt">Project</phoneme>'
        elif combined_sentences_token_list[i][0] == "project" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɑˌdʒɛkt">project</phoneme>'

        elif combined_sentences_token_list[i][0] == "Project" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prəˈdʒɛkt">Project</phoneme>'
        elif combined_sentences_token_list[i][0] == "project" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prəˈdʒɛkt">project</phoneme>'
        elif combined_sentences_token_list[i][0] == "Project" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɒdʒɛkt">Project</phoneme>'
        elif combined_sentences_token_list[i][0] == "project" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɒdʒɛkt">project</phoneme>'
    return combined_sentences_word_list

def proofread(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Proofread" and combined_sentences_token_list[i][1] in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpruːfˌriːd">Proofread</phoneme>'
        elif combined_sentences_token_list[i][0] == "proofread" and combined_sentences_token_list[i][1] in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpruːfˌriːd">proofread</phoneme>'
        elif combined_sentences_token_list[i][0] == "Proofread" and combined_sentences_token_list[i][1] not in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpruːfˌrɛd">Proofread</phoneme>'
        elif combined_sentences_token_list[i][0] == "proofread" and combined_sentences_token_list[i][1] not in ["VB", "VBP", "VBZ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpruːfˌrɛd">proofread</phoneme>'
    return combined_sentences_word_list

#Only in British English, because the verb and noun are pronounced the same in American English.
def prospect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Prospect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prəˈspɛkt">Prospect</phoneme>'
        elif combined_sentences_token_list[i][0] == "prospect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prəˈspɛkt">prospect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Prospect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɒspɛkt">Prospect</phoneme>'
        elif combined_sentences_token_list[i][0] == "prospect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprɒspɛkt">prospect</phoneme>'
    return combined_sentences_word_list

def protest(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Protest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="proʊˈtɛst">Protest</phoneme>'
        elif combined_sentences_token_list[i][0] == "protest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="proʊˈtɛst">protest</phoneme>'
        elif combined_sentences_token_list[i][0] == "Protest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈproʊˌtɛst">Protest</phoneme>'
        elif combined_sentences_token_list[i][0] == "protest" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈproʊˌtɛst">protest</phoneme>'

        elif combined_sentences_token_list[i][0] == "Protest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prəˈtɛst">Protest</phoneme>'
        elif combined_sentences_token_list[i][0] == "protest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="prəˈtɛst">protest</phoneme>'
        elif combined_sentences_token_list[i][0] == "Protest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprəʊtɛst">Protest</phoneme>'
        elif combined_sentences_token_list[i][0] == "protest" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈprəʊtɛst">protest</phoneme>'
    return combined_sentences_word_list

def pussy(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Pussy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpʌsi">Pussy</phoneme>'
        elif combined_sentences_token_list[i][0] == "pussy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpʌsi">pussy</phoneme>'
        elif combined_sentences_token_list[i][0] == "Pussy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpusi">Pussy</phoneme>'
        elif combined_sentences_token_list[i][0] == "pussy" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpusi">pussy</phoneme>'

        elif combined_sentences_token_list[i][0] == "Pussy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpʌsɪ">Pussy</phoneme>'
        elif combined_sentences_token_list[i][0] == "pussy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpʌsɪ">pussy</phoneme>'
        elif combined_sentences_token_list[i][0] == "Pussy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpʊsɪ">Pussy</phoneme>'
        elif combined_sentences_token_list[i][0] == "pussy" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpʊsɪ">pussy</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def putting(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Putting" and combined_sentences_token_list[i][3].lower() == "putt":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpʌtɪŋ">Putting</phoneme>'
        elif combined_sentences_token_list[i][0] == "putting" and combined_sentences_token_list[i][3].lower() == "putt":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpʌtɪŋ">putting</phoneme>'
        elif combined_sentences_token_list[i][0] == "Putting" and combined_sentences_token_list[i][3].lower() == "put":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpʊtɪŋ">Putting</phoneme>'
        elif combined_sentences_token_list[i][0] == "putting" and combined_sentences_token_list[i][3].lower() == "put":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈpʊtɪŋ">putting</phoneme>'
    return combined_sentences_word_list

#As the different forms of the noun "raven" (as in "ravin" or as the bird) have different pronounciations,
#only the adjective and verb are included.
def raven(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Raven" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrævən">Raven</phoneme>'
        elif combined_sentences_token_list[i][0] == "raven" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrævən">raven</phoneme>'
        elif combined_sentences_token_list[i][0] == "Raven" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈreɪvən">Raven</phoneme>'
        elif combined_sentences_token_list[i][0] == "raven" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈreɪvən">raven</phoneme>'
    return combined_sentences_word_list

def read(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Read" and combined_sentences_token_list[i][1] in ["VB", "VBP", "VBZ", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːd">Read</phoneme>'
        elif combined_sentences_token_list[i][0] == "read" and combined_sentences_token_list[i][1] in ["VB", "VBP", "VBZ", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːd">read</phoneme>'
        elif combined_sentences_token_list[i][0] == "Read" and combined_sentences_token_list[i][1] not in ["VB", "VBP", "VBZ", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɛd">Read</phoneme>'
        elif combined_sentences_token_list[i][0] == "read" and combined_sentences_token_list[i][1] not in ["VB", "VBP", "VBZ", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɛd">read</phoneme>'
    return combined_sentences_word_list

def rebel(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Rebel" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈbɛl">Rebel</phoneme>'
        elif combined_sentences_token_list[i][0] == "rebel" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈbɛl">rebel</phoneme>'
        elif combined_sentences_token_list[i][0] == "Rebel" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrɛbəl">Rebel</phoneme>'
        elif combined_sentences_token_list[i][0] == "rebel" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrɛbəl">rebel</phoneme>'
    return combined_sentences_word_list

#As the "recall" verb form meaning "to remove from office" is pronounced differently from the other transitive verb forms in American English,
#only the noun is included in American English.
def recall(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Recall" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌkɔl">Recall</phoneme>'
        elif combined_sentences_token_list[i][0] == "recall" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌkɔl">recall</phoneme>'

        elif combined_sentences_token_list[i][0] == "Recall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈkɔːl">Recall</phoneme>'
        elif combined_sentences_token_list[i][0] == "recall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈkɔːl">recall</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːkɔːl">Recall</phoneme>'
        elif combined_sentences_token_list[i][0] == "recall" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːkɔːl">recall</phoneme>'
    return combined_sentences_word_list

def recap(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Recap" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈkæp">Recap</phoneme>'
        elif combined_sentences_token_list[i][0] == "recap" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈkæp">recap</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recap" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌkæp">Recap</phoneme>'
        elif combined_sentences_token_list[i][0] == "recap" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌkæp">recap</phoneme>'

        elif combined_sentences_token_list[i][0] == "Recap" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈkæp">Recap</phoneme>'
        elif combined_sentences_token_list[i][0] == "recap" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈkæp">recap</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recap" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌkæp">Recap</phoneme>'
        elif combined_sentences_token_list[i][0] == "recap" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌkæp">recap</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def recess(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Recess" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈsɛs">Recess</phoneme>'
        elif combined_sentences_token_list[i][0] == "recess" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈsɛs">recess</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recess" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrisɛs">Recess</phoneme>'
        elif combined_sentences_token_list[i][0] == "recess" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrisɛs">recess</phoneme>'

        elif combined_sentences_token_list[i][0] == "Recess" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈsɛs">Recess</phoneme>'
        elif combined_sentences_token_list[i][0] == "recess" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈsɛs">recess</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recess" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːsɛs">Recess</phoneme>'
        elif combined_sentences_token_list[i][0] == "recess" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːsɛs">recess</phoneme>'
    return combined_sentences_word_list

#Only in British English, as the noun and adjective are pronounced the same in American English.
def recitative(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Recitative" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌrɛsɪtəˈtiːv">Recitative</phoneme>'
        elif combined_sentences_token_list[i][0] == "recitative" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌrɛsɪtəˈtiːv">recitative</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recitative" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈsaɪtətɪv">Recitative</phoneme>'
        elif combined_sentences_token_list[i][0] == "recitative" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈsaɪtətɪv">recitative</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def recoil(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Recoil" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈkɔɪl">Recoil</phoneme>'
        elif combined_sentences_token_list[i][0] == "recoil" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈkɔɪl">recoil</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recoil" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌkɔɪl">Recoil</phoneme>'
        elif combined_sentences_token_list[i][0] == "recoil" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌkɔɪl">recoil</phoneme>'

        elif combined_sentences_token_list[i][0] == "Recoil" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈkɔɪl">Recoil</phoneme>'
        elif combined_sentences_token_list[i][0] == "recoil" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈkɔɪl">recoil</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recoil" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːkɔɪl">Recoil</phoneme>'
        elif combined_sentences_token_list[i][0] == "recoil" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːkɔɪl">recoil</phoneme>'
    return combined_sentences_word_list

def recollect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Recollect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌrɛkəˈlɛkt">Recollect</phoneme>'
        elif combined_sentences_token_list[i][0] == "recollect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˌrɛkəˈlɛkt">recollect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Recollect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrekəˌlekt">Recollect</phoneme>'
        elif combined_sentences_token_list[i][0] == "recollect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrekəˌlekt">recollect</phoneme>'
    return combined_sentences_word_list

def record(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Record" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈkɔrd">Record</phoneme>'
        elif combined_sentences_token_list[i][0] == "record" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈkɔrd">record</phoneme>'
        elif combined_sentences_token_list[i][0] == "Record" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrɛkərd">Record</phoneme>'
        elif combined_sentences_token_list[i][0] == "record" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrɛkərd">record</phoneme>'

        elif combined_sentences_token_list[i][0] == "Record" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈkɔːd">Record</phoneme>'
        elif combined_sentences_token_list[i][0] == "record" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈkɔːd">record</phoneme>'
        elif combined_sentences_token_list[i][0] == "Record" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrɛkɔːd">Record</phoneme>'
        elif combined_sentences_token_list[i][0] == "record" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrɛkɔːd">record</phoneme>'
    return combined_sentences_word_list

#Only in American English, as the verb and noun are pronounced the same in British English.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def redress(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Redress" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈdrɛs">Redress</phoneme>'
        elif combined_sentences_token_list[i][0] == "redress" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈdrɛs">redress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Redress" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌdrɛs">Redress</phoneme>'
        elif combined_sentences_token_list[i][0] == "redress" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌdrɛs">redress</phoneme>'
    return combined_sentences_word_list

def refill(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Refill" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈfɪl">Refill</phoneme>'
        elif combined_sentences_token_list[i][0] == "refill" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈfɪl">refill</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refill" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌfɪl">Refill</phoneme>'
        elif combined_sentences_token_list[i][0] == "refill" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌfɪl">refill</phoneme>'

        elif combined_sentences_token_list[i][0] == "Refill" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈfɪl">Refill</phoneme>'
        elif combined_sentences_token_list[i][0] == "refill" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈfɪl">refill</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refill" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːfɪl">Refill</phoneme>'
        elif combined_sentences_token_list[i][0] == "refill" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːfɪl">refill</phoneme>'
    return combined_sentences_word_list

def refit(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Refit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈfɪt">Refit</phoneme>'
        elif combined_sentences_token_list[i][0] == "refit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈfɪt">refit</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌfɪt">Refit</phoneme>'
        elif combined_sentences_token_list[i][0] == "refit" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌfɪt">refit</phoneme>'

        elif combined_sentences_token_list[i][0] == "Refit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈfɪt">Refit</phoneme>'
        elif combined_sentences_token_list[i][0] == "refit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈfɪt">refit</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌfɪt">Refit</phoneme>'
        elif combined_sentences_token_list[i][0] == "refit" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌfɪt">refit</phoneme>'
    return combined_sentences_word_list

def reflex(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Reflex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈflɛks">Reflex</phoneme>'
        elif combined_sentences_token_list[i][0] == "reflex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈflɛks">reflex</phoneme>'
        elif combined_sentences_token_list[i][0] == "Reflex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌflɛks">Reflex</phoneme>'
        elif combined_sentences_token_list[i][0] == "reflex" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌflɛks">reflex</phoneme>'

        elif combined_sentences_token_list[i][0] == "Reflex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈflɛks">Reflex</phoneme>'
        elif combined_sentences_token_list[i][0] == "reflex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈflɛks">reflex</phoneme>'
        elif combined_sentences_token_list[i][0] == "Reflex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːflɛks">Reflex</phoneme>'
        elif combined_sentences_token_list[i][0] == "reflex" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːflɛks">reflex</phoneme>'
    return combined_sentences_word_list

def refund(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Refund" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈfʌnd">Refund</phoneme>'
        elif combined_sentences_token_list[i][0] == "refund" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈfʌnd">refund</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refund" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌfʌnd">Refund</phoneme>'
        elif combined_sentences_token_list[i][0] == "refund" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌfʌnd">refund</phoneme>'

        elif combined_sentences_token_list[i][0] == "Refund" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈfʌnd">Refund</phoneme>'
        elif combined_sentences_token_list[i][0] == "refund" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈfʌnd">refund</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refund" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌfʌnd">Refund</phoneme>'
        elif combined_sentences_token_list[i][0] == "refund" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌfʌnd">refund</phoneme>'
    return combined_sentences_word_list

def refuse(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Refuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈfjuz">Refuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "refuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈfjuz">refuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrɛfjus">Refuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "refuse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrɛfjus">refuse</phoneme>'

        elif combined_sentences_token_list[i][0] == "Refuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈfjuːz">Refuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "refuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈfjuːz">refuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Refuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrɛfjuːs">Refuse</phoneme>'
        elif combined_sentences_token_list[i][0] == "refuse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrɛfjuːs">refuse</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def regenerate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Regenerate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈdʒɛnəˌreɪt">Regenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "regenerate" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈdʒɛnəˌreɪt">regenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Regenerate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈdʒɛnərɪt">Regenerate</phoneme>'
        elif combined_sentences_token_list[i][0] == "regenerate" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈdʒɛnərɪt">regenerate</phoneme>'
    return combined_sentences_word_list

def regress(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Regress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈgrɛs">Regress</phoneme>'
        elif combined_sentences_token_list[i][0] == "regress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈgrɛs">regress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Regress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrigrɛs">Regress</phoneme>'
        elif combined_sentences_token_list[i][0] == "regress" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrigrɛs">regress</phoneme>'

        elif combined_sentences_token_list[i][0] == "Regress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈɡrɛs">Regress</phoneme>'
        elif combined_sentences_token_list[i][0] == "regress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈɡrɛs">regress</phoneme>'
        elif combined_sentences_token_list[i][0] == "Regress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːɡrɛs">Regress</phoneme>'
        elif combined_sentences_token_list[i][0] == "regress" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːɡrɛs">regress</phoneme>'
    return combined_sentences_word_list

#As the verb may be pronounced either way in American English, only the noun was included.
def rehash(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Rehash" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌhæʃ">Rehash</phoneme>'
        elif combined_sentences_token_list[i][0] == "rehash" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌhæʃ">rehash</phoneme>'

        elif combined_sentences_token_list[i][0] == "Rehash" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈhæʃ">Rehash</phoneme>'
        elif combined_sentences_token_list[i][0] == "rehash" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈhæʃ">rehash</phoneme>'
        elif combined_sentences_token_list[i][0] == "Rehash" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌhæʃ">Rehash</phoneme>'
        elif combined_sentences_token_list[i][0] == "rehash" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌhæʃ">rehash</phoneme>'
    return combined_sentences_word_list

def reject(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Reject" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈdʒɛkt">Reject</phoneme>'
        elif combined_sentences_token_list[i][0] == "reject" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈdʒɛkt">reject</phoneme>'
        elif combined_sentences_token_list[i][0] == "Reject" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈridʒɛkt">Reject</phoneme>'
        elif combined_sentences_token_list[i][0] == "reject" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈridʒɛkt">reject</phoneme>'

        elif combined_sentences_token_list[i][0] == "Reject" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈdʒɛkt">Reject</phoneme>'
        elif combined_sentences_token_list[i][0] == "reject" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈdʒɛkt">reject</phoneme>'
        elif combined_sentences_token_list[i][0] == "Reject" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːdʒɛkt">Reject</phoneme>'
        elif combined_sentences_token_list[i][0] == "reject" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːdʒɛkt">reject</phoneme>'
    return combined_sentences_word_list

def relapse(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Relapse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈlæps">Relapse</phoneme>'
        elif combined_sentences_token_list[i][0] == "relapse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈlæps">relapse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Relapse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrilæps">Relapse</phoneme>'
        elif combined_sentences_token_list[i][0] == "relapse" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈrilæps">relapse</phoneme>'

        elif combined_sentences_token_list[i][0] == "Relapse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈlæps">Relapse</phoneme>'
        elif combined_sentences_token_list[i][0] == "relapse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈlæps">relapse</phoneme>'
        elif combined_sentences_token_list[i][0] == "Relapse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌlæps">Relapse</phoneme>'
        elif combined_sentences_token_list[i][0] == "relapse" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌlæps">relapse</phoneme>'
    return combined_sentences_word_list

def relay(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Relay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈleɪ">Relay</phoneme>'
        elif combined_sentences_token_list[i][0] == "relay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈleɪ">relay</phoneme>'
        elif combined_sentences_token_list[i][0] == "Relay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌleɪ">Relay</phoneme>'
        elif combined_sentences_token_list[i][0] == "relay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌleɪ">relay</phoneme>'

        elif combined_sentences_token_list[i][0] == "Relay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈleɪ">Relay</phoneme>'
        elif combined_sentences_token_list[i][0] == "relay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈleɪ">relay</phoneme>'
        elif combined_sentences_token_list[i][0] == "Relay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːleɪ">Relay</phoneme>'
        elif combined_sentences_token_list[i][0] == "relay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːleɪ">relay</phoneme>'
    return combined_sentences_word_list

def remake(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Remake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈmeɪk">Remake</phoneme>'
        elif combined_sentences_token_list[i][0] == "remake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈmeɪk">remake</phoneme>'
        elif combined_sentences_token_list[i][0] == "Remake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌmeɪk">Remake</phoneme>'
        elif combined_sentences_token_list[i][0] == "remake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌmeɪk">remake</phoneme>'

        elif combined_sentences_token_list[i][0] == "Remake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈmeɪk">Remake</phoneme>'
        elif combined_sentences_token_list[i][0] == "remake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈmeɪk">remake</phoneme>'
        elif combined_sentences_token_list[i][0] == "Remake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌmeɪk">Remake</phoneme>'
        elif combined_sentences_token_list[i][0] == "remake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌmeɪk">remake</phoneme>'
    return combined_sentences_word_list

def repatriate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Repatriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈpeɪtriˌeɪt">Repatriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "repatriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈpeɪtriˌeɪt">repatriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Repatriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈpeɪtriɪt">Repatriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "repatriate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈpeɪtriɪt">repatriate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Repatriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈpætrɪˌeɪt">Repatriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "repatriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈpætrɪˌeɪt">repatriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Repatriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈpætrɪɪt">Repatriate</phoneme>'
        elif combined_sentences_token_list[i][0] == "repatriate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈpætrɪɪt">repatriate</phoneme>'
    return combined_sentences_word_list

def repent(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Repent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈpɛnt">Repent</phoneme>'
        elif combined_sentences_token_list[i][0] == "repent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈpɛnt">repent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Repent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈripən">Repent</phoneme>'
        elif combined_sentences_token_list[i][0] == "repent" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈripən">repent</phoneme>'

        elif combined_sentences_token_list[i][0] == "Repent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈpɛnt">Repent</phoneme>'
        elif combined_sentences_token_list[i][0] == "repent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈpɛnt">repent</phoneme>'
        elif combined_sentences_token_list[i][0] == "Repent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːpənt">Repent</phoneme>'
        elif combined_sentences_token_list[i][0] == "repent" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːpənt">repent</phoneme>'
    return combined_sentences_word_list

def replay(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Replay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈpleɪ">Replay</phoneme>'
        elif combined_sentences_token_list[i][0] == "replay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈpleɪ">replay</phoneme>'
        elif combined_sentences_token_list[i][0] == "Replay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌpleɪ">Replay</phoneme>'
        elif combined_sentences_token_list[i][0] == "replay" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌpleɪ">replay</phoneme>'

        elif combined_sentences_token_list[i][0] == "Replay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈplei">Replay</phoneme>'
        elif combined_sentences_token_list[i][0] == "replay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈplei">replay</phoneme>'
        elif combined_sentences_token_list[i][0] == "Replay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌplei">Replay</phoneme>'
        elif combined_sentences_token_list[i][0] == "replay" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌplei">replay</phoneme>'
    return combined_sentences_word_list

def reprint(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Reprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈprɪnt">Reprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "reprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈprɪnt">reprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "Reprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌprɪnt">Reprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "reprint" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌprɪnt">reprint</phoneme>'

        elif combined_sentences_token_list[i][0] == "Reprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈprɪnt">Reprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "reprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈprɪnt">reprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "Reprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌprɪnt">Reprint</phoneme>'
        elif combined_sentences_token_list[i][0] == "reprint" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌprɪnt">reprint</phoneme>'
    return combined_sentences_word_list

def rerun(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Rerun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈrʌn">Rerun</phoneme>'
        elif combined_sentences_token_list[i][0] == "rerun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈrʌn">rerun</phoneme>'
        elif combined_sentences_token_list[i][0] == "Rerun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌrʌn">Rerun</phoneme>'
        elif combined_sentences_token_list[i][0] == "rerun" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌrʌn">rerun</phoneme>'

        elif combined_sentences_token_list[i][0] == "Rerun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈrʌn">Rerun</phoneme>'
        elif combined_sentences_token_list[i][0] == "rerun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈrʌn">rerun</phoneme>'
        elif combined_sentences_token_list[i][0] == "Rerun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌrʌn">Rerun</phoneme>'
        elif combined_sentences_token_list[i][0] == "rerun" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌrʌn">rerun</phoneme>'
    return combined_sentences_word_list

def retake(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Retake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈteɪk">Retake</phoneme>'
        elif combined_sentences_token_list[i][0] == "retake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈteɪk">retake</phoneme>'
        elif combined_sentences_token_list[i][0] == "Retake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌteɪk">Retake</phoneme>'
        elif combined_sentences_token_list[i][0] == "retake" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌteɪk">retake</phoneme>'

        elif combined_sentences_token_list[i][0] == "Retake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈteɪk">Retake</phoneme>'
        elif combined_sentences_token_list[i][0] == "retake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈteɪk">retake</phoneme>'
        elif combined_sentences_token_list[i][0] == "Retake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌteɪk">Retake</phoneme>'
        elif combined_sentences_token_list[i][0] == "retake" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌteɪk">retake</phoneme>'
    return combined_sentences_word_list

#As different forms of the noun "retard" are pronounced differently in American English, only the verb is included.
def retard(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Retard" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈtɑːrd">Retard</phoneme>'
        elif combined_sentences_token_list[i][0] == "retard" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈtɑːrd">retard</phoneme>'

        elif combined_sentences_token_list[i][0] == "Retard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈtɑːd">Retard</phoneme>'
        elif combined_sentences_token_list[i][0] == "retard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="rɪˈtɑːd">retard</phoneme>'
        elif combined_sentences_token_list[i][0] == "Retard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːtɑːd">Retard</phoneme>'
        elif combined_sentences_token_list[i][0] == "retard" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːtɑːd">retard</phoneme>'
    return combined_sentences_word_list

def rewind(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Rewind" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈwaɪnd">Rewind</phoneme>'
        elif combined_sentences_token_list[i][0] == "rewind" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riˈwaɪnd">rewind</phoneme>'
        elif combined_sentences_token_list[i][0] == "Rewind" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌwaɪnd">Rewind</phoneme>'
        elif combined_sentences_token_list[i][0] == "rewind" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriˌwaɪnd">rewind</phoneme>'

        elif combined_sentences_token_list[i][0] == "Rewind" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈwaɪnd">Rewind</phoneme>'
        elif combined_sentences_token_list[i][0] == "rewind" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="riːˈwaɪnd">rewind</phoneme>'
        elif combined_sentences_token_list[i][0] == "Rewind" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌwaɪnd">Rewind</phoneme>'
        elif combined_sentences_token_list[i][0] == "rewind" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈriːˌwaɪnd">rewind</phoneme>'
    return combined_sentences_word_list

def segment(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Segment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɛgmɛnt">Segment</phoneme>'
        elif combined_sentences_token_list[i][0] == "segment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɛgmɛnt">segment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Segment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɛgmənt">Segment</phoneme>'
        elif combined_sentences_token_list[i][0] == "segment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɛgmənt">segment</phoneme>'

        elif combined_sentences_token_list[i][0] == "Segment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="sɛɡˈmɛnt">Segment</phoneme>'
        elif combined_sentences_token_list[i][0] == "segment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="sɛɡˈmɛnt">segment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Segment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɛɡmənt">Segment</phoneme>'
        elif combined_sentences_token_list[i][0] == "segment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɛɡmənt">segment</phoneme>'
    return combined_sentences_word_list

def separate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Separate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsepəˌreit">Separate</phoneme>'
        elif combined_sentences_token_list[i][0] == "separate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsepəˌreit">separate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Separate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsepərɪt">Separate</phoneme>'
        elif combined_sentences_token_list[i][0] == "separate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsepərɪt">separate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Separate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɛpəˌreɪt">Separate</phoneme>'
        elif combined_sentences_token_list[i][0] == "separate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɛpəˌreɪt">separate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Separate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɛpərɪt">Separate</phoneme>'
        elif combined_sentences_token_list[i][0] == "separate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɛpərɪt">separate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def skied(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Skied" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i][3].lower() == "ski":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="skiːd">Skied</phoneme>'
        elif combined_sentences_token_list[i][0] == "skied" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i][3].lower() == "ski":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="skiːd">skied</phoneme>'
        elif combined_sentences_token_list[i][0] == "Skied" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i][3].lower() == "sky":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="skaɪd">Skied</phoneme>'
        elif combined_sentences_token_list[i][0] == "skied" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i][3].lower() == "sky":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="skaɪd">skied</phoneme>'
    return combined_sentences_word_list

def sow(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Sow" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="soʊ">Sow</phoneme>'
        elif combined_sentences_token_list[i][0] == "sow" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="soʊ">sow</phoneme>'
        elif combined_sentences_token_list[i][0] == "Sow" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="saʊ">Sow</phoneme>'
        elif combined_sentences_token_list[i][0] == "sow" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="saʊ">sow</phoneme>'

        elif combined_sentences_token_list[i][0] == "Sow" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səʊ">Sow</phoneme>'
        elif combined_sentences_token_list[i][0] == "sow" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səʊ">sow</phoneme>'
        elif combined_sentences_token_list[i][0] == "Sow" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="saʊ">Sow</phoneme>'
        elif combined_sentences_token_list[i][0] == "sow" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="saʊ">sow</phoneme>'
    return combined_sentences_word_list

#Only in American English, as the noun and adjective are pronounced the same in British English.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def stabile(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Stabile" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsteɪ bil">Stabile</phoneme>'
        elif combined_sentences_token_list[i][0] == "stabile" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsteɪ bil">stabile</phoneme>'
        elif combined_sentences_token_list[i][0] == "Stabile" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsteɪbɪl">Stabile</phoneme>'
        elif combined_sentences_token_list[i][0] == "stabile" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsteɪbɪl">stabile</phoneme>'
    return combined_sentences_word_list

def stipulate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Stipulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈstɪpjəˌleɪt">Stipulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "stipulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈstɪpjəˌleɪt">stipulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Stipulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈstɪpjʊlɪt">Stipulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "stipulate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈstɪpjʊlɪt">stipulate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Stipulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈstɪpjʊˌleɪt">Stipulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "stipulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈstɪpjʊˌleɪt">stipulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Stipulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈstɪpjʊlɪt">Stipulate</phoneme>'
        elif combined_sentences_token_list[i][0] == "stipulate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈstɪpjʊlɪt">stipulate</phoneme>'
    return combined_sentences_word_list

def subject(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Subject" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səbˈdʒɛkt">Subject</phoneme>'
        elif combined_sentences_token_list[i][0] == "subject" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səbˈdʒɛkt">subject</phoneme>'
        elif combined_sentences_token_list[i][0] == "Subject" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsʌbdʒɪkt">Subject</phoneme>'
        elif combined_sentences_token_list[i][0] == "subject" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsʌbdʒɪkt">subject</phoneme>'
    return combined_sentences_word_list

#The POS was used instead of the TAG for the adverbs, as the first letters of the various adverb tags differ.
#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def supply(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Supply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈplaɪ">Supply</phoneme>'
        elif combined_sentences_token_list[i][0] == "supply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈplaɪ">supply</phoneme>'
        elif combined_sentences_token_list[i][0] == "Supply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsʌpli">Supply</phoneme>'
        elif combined_sentences_token_list[i][0] == "supply" and English_Phonetics == "American_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsʌpli">supply</phoneme>'

        elif combined_sentences_token_list[i][0] == "Supply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈplaɪ">Supply</phoneme>'
        elif combined_sentences_token_list[i][0] == "supply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈplaɪ">supply</phoneme>'
        elif combined_sentences_token_list[i][0] == "Supply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsʌplɪ">Supply</phoneme>'
        elif combined_sentences_token_list[i][0] == "supply" and English_Phonetics == "British_English" and combined_sentences_token_list[i][2][:3] == "ADV":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsʌplɪ">supply</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
#Supposed in "was supposed to" is a modal verb and could be identified by the Spacy fine grained tag "MD" or if the following word is "to".
def supposed(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Supposed" and (combined_sentences_token_list[i][1][:2] == "MD" or combined_sentences_token_list[i+1][0].lower() == "to"):
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈpoʊst">Supposed</phoneme>'
        elif combined_sentences_token_list[i][0] == "supposed" and (combined_sentences_token_list[i][1][:2] == "MD" or combined_sentences_token_list[i+1][0].lower() == "to"):
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈpoʊst">supposed</phoneme>'
        elif combined_sentences_token_list[i][0] == "Supposed" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈpoʊzd">Supposed</phoneme>'
        elif combined_sentences_token_list[i][0] == "supposed" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈpoʊzd">supposed</phoneme>'
        elif combined_sentences_token_list[i][0] == "Supposed" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈpoʊz(ɪ)d">Supposed</phoneme>'
        elif combined_sentences_token_list[i][0] == "supposed" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈpoʊz(ɪ)d">supposed</phoneme>'
    return combined_sentences_word_list

def survey(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Survey" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="sərˈveɪ">Survey</phoneme>'
        elif combined_sentences_token_list[i][0] == "survey" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="sərˈveɪ">survey</phoneme>'
        elif combined_sentences_token_list[i][0] == "Survey" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɜrˌveɪ">Survey</phoneme>'
        elif combined_sentences_token_list[i][0] == "survey" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɜrˌveɪ">survey</phoneme>'

        elif combined_sentences_token_list[i][0] == "Survey" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="sɜːˈveɪ">Survey</phoneme>'
        elif combined_sentences_token_list[i][0] == "survey" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="sɜːˈveɪ">survey</phoneme>'
        elif combined_sentences_token_list[i][0] == "Survey" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɜːveɪ">Survey</phoneme>'
        elif combined_sentences_token_list[i][0] == "survey" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɜːveɪ">survey</phoneme>'
    return combined_sentences_word_list

def suspect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Suspect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈspɛkt">Suspect</phoneme>'
        elif combined_sentences_token_list[i][0] == "suspect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈspɛkt">suspect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Suspect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsʌsˌpɛkt">Suspect</phoneme>'
        elif combined_sentences_token_list[i][0] == "suspect" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsʌsˌpɛkt">suspect</phoneme>'

        elif combined_sentences_token_list[i][0] == "Suspect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈspɛkt">Suspect</phoneme>'
        elif combined_sentences_token_list[i][0] == "suspect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="səˈspɛkt">suspect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Suspect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsʌspɛkt">Suspect</phoneme>'
        elif combined_sentences_token_list[i][0] == "suspect" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["NN", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsʌspɛkt">suspect</phoneme>'
    return combined_sentences_word_list

def syndicate(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Syndicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɪndəˌkeɪt">Syndicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "syndicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɪndəˌkeɪt">syndicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Syndicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɪndəkɪt">Syndicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "syndicate" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɪndəkɪt">syndicate</phoneme>'

        elif combined_sentences_token_list[i][0] == "Syndicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɪndɪˌkeɪt">Syndicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "syndicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɪndɪˌkeɪt">syndicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "Syndicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɪndɪkɪt">Syndicate</phoneme>'
        elif combined_sentences_token_list[i][0] == "syndicate" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈsɪndɪkɪt">syndicate</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def tarry(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Tarry" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtæri">Tarry</phoneme>'
        elif combined_sentences_token_list[i][0] == "tarry" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtæri">tarry</phoneme>'
        elif combined_sentences_token_list[i][0] == "Tarry" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtɑri">Tarry</phoneme>'
        elif combined_sentences_token_list[i][0] == "tarry" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtɑri">tarry</phoneme>'

        elif combined_sentences_token_list[i][0] == "Tarry" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtærɪ">Tarry</phoneme>'
        elif combined_sentences_token_list[i][0] == "tarry" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtærɪ">tarry</phoneme>'
        elif combined_sentences_token_list[i][0] == "Tarry" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtɑrɪ">Tarry</phoneme>'
        elif combined_sentences_token_list[i][0] == "tarry" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtɑri">tarry</phoneme>'
    return combined_sentences_word_list

#The nouns "tear" (liquid tear and tear in clothes) cannot be distinguished by Spacy, so phoneme substitutions will
#only take place if the fine-grained tag is "VB" (verb).
def tear(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Tear" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtɛr">Tear</phoneme>'
        elif combined_sentences_token_list[i][0] == "tear" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtɛr">tear</phoneme>'

        elif combined_sentences_token_list[i][0] == "Tear" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtɛə">Tear</phoneme>'
        elif combined_sentences_token_list[i][0] == "tear" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtɛə">tear</phoneme>'
    return combined_sentences_word_list

def torment(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Torment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tɔrˈmɛnt">Torment</phoneme>'
        elif combined_sentences_token_list[i][0] == "torment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tɔrˈmɛnt">torment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Torment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtɔrˌmɛnt">Torment</phoneme>'
        elif combined_sentences_token_list[i][0] == "torment" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtɔrˌmɛnt">torment</phoneme>'

        elif combined_sentences_token_list[i][0] == "Torment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tɔːˈmɛnt">Torment</phoneme>'
        elif combined_sentences_token_list[i][0] == "torment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="tɔːˈmɛnt">torment</phoneme>'
        elif combined_sentences_token_list[i][0] == "Torment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtɔːmɛnt">Torment</phoneme>'
        elif combined_sentences_token_list[i][0] == "torment" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtɔːmɛnt">torment</phoneme>'
    return combined_sentences_word_list

def transect(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Transect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="trænˈsɛkt">Transect</phoneme>'
        elif combined_sentences_token_list[i][0] == "transect" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="trænˈsɛkt">transect</phoneme>'
        elif combined_sentences_token_list[i][0] == "Transect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtrænsɛkt">Transect</phoneme>'
        elif combined_sentences_token_list[i][0] == "transect" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtrænsɛkt">transect</phoneme>'
    return combined_sentences_word_list

#Only for British English, since the verb and noun may be pronounced the same way in American English.
def transfer(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Transfer" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="trænsˈfɜː">Transfer</phoneme>'
        elif combined_sentences_token_list[i][0] == "transfer" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="trænsˈfɜː">transfer</phoneme>'
        elif combined_sentences_token_list[i][0] == "Transfer" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtrænsfɜː">Transfer</phoneme>'
        elif combined_sentences_token_list[i][0] == "transfer" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtrænsfɜː">transfer</phoneme>'
    return combined_sentences_word_list

def transplant(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Transplant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="trænsˈplænt">Transplant</phoneme>'
        elif combined_sentences_token_list[i][0] == "transplant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="trænsˈplænt">transplant</phoneme>'
        elif combined_sentences_token_list[i][0] == "Transplant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtrænsˌplænt">Transplant</phoneme>'
        elif combined_sentences_token_list[i][0] == "transplant" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtrænsˌplænt">transplant</phoneme>'

        elif combined_sentences_token_list[i][0] == "Transplant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="trænsˈplɑːnt">Transplant</phoneme>'
        elif combined_sentences_token_list[i][0] == "transplant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="trænsˈplɑːnt">transplant</phoneme>'
        elif combined_sentences_token_list[i][0] == "Transplant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtrænsˌplɑːnt">Transplant</phoneme>'
        elif combined_sentences_token_list[i][0] == "transplant" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtrænsˌplɑːnt">transplant</phoneme>'
    return combined_sentences_word_list

def transport(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Transport" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="trænsˈpɔrt">Transport</phoneme>'
        elif combined_sentences_token_list[i][0] == "transport" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="trænsˈpɔrt">transport</phoneme>'
        elif combined_sentences_token_list[i][0] == "Transport" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtrænsˌpɔrt">Transport</phoneme>'
        elif combined_sentences_token_list[i][0] == "transport" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtrænsˌpɔrt">transport</phoneme>'

        elif combined_sentences_token_list[i][0] == "Transport" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="trænsˈpɔːt">Transport</phoneme>'
        elif combined_sentences_token_list[i][0] == "transport" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="trænsˈpɔːt">transport</phoneme>'
        elif combined_sentences_token_list[i][0] == "Transport" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtrænsˌpɔːt">Transport</phoneme>'
        elif combined_sentences_token_list[i][0] == "transport" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈtrænsˌpɔːt">transport</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def upset(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Upset" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ʌpˈsɛt">Upset</phoneme>'
        elif combined_sentences_token_list[i][0] == "upset" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ʌpˈsɛt">upset</phoneme>'
        elif combined_sentences_token_list[i][0] == "Upset" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈʌpˌsɛt">Upset</phoneme>'
        elif combined_sentences_token_list[i][0] == "upset" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈʌpˌsɛt">upset</phoneme>'

        elif combined_sentences_token_list[i][0] == "Upset" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ʌpˈsɛt">Upset</phoneme>'
        elif combined_sentences_token_list[i][0] == "upset" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ʌpˈsɛt">upset</phoneme>'
        elif combined_sentences_token_list[i][0] == "Upset" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈʌpˌsɛt">Upset</phoneme>'
        elif combined_sentences_token_list[i][0] == "upset" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈʌpˌsɛt">upset</phoneme>'
    return combined_sentences_word_list

def use(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Use" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="juz">Use</phoneme>'
        elif combined_sentences_token_list[i][0] == "use" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="juz">use</phoneme>'
        elif combined_sentences_token_list[i][0] == "Use" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="jus">Use</phoneme>'
        elif combined_sentences_token_list[i][0] == "use" and English_Phonetics == "American_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="jus">use</phoneme>'

        elif combined_sentences_token_list[i][0] == "Use" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="juːz">Use</phoneme>'
        elif combined_sentences_token_list[i][0] == "use" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="juːz">use</phoneme>'
        elif combined_sentences_token_list[i][0] == "Use" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="juːs">Use</phoneme>'
        elif combined_sentences_token_list[i][0] == "use" and English_Phonetics == "British_English" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="juːs">use</phoneme>'
    return combined_sentences_word_list

#Supposed in "was supposed to" is a modal verb and could be identified by the Spacy fine grained tag "MD" or if the following word is "to".
def used(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Used" and (combined_sentences_token_list[i][1][:2] == "MD" or combined_sentences_token_list[i+1][0].lower() == "to"):
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="juːst">Used</phoneme>'
        elif combined_sentences_token_list[i][0] == "used" and (combined_sentences_token_list[i][1][:2] == "MD" or combined_sentences_token_list[i+1][0].lower() == "to"):
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="juːst">used</phoneme>'
        elif combined_sentences_token_list[i][0] == "Used" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="juːzd">Used</phoneme>'
        elif combined_sentences_token_list[i][0] == "used" and combined_sentences_token_list[i][1][:2] in ["VB", "JJ"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="juːzd">used</phoneme>'
    return combined_sentences_word_list

def wicked(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Wicked" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈwɪkt">Wicked</phoneme>'
        elif combined_sentences_token_list[i][0] == "wicked" and combined_sentences_token_list[i][1][:2] == "VB":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈwɪkt">wicked</phoneme>'
        elif combined_sentences_token_list[i][0] == "Wicked" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈwɪkɪd">Wicked</phoneme>'
        elif combined_sentences_token_list[i][0] == "wicked" and combined_sentences_token_list[i][1][:2] == "JJ":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈwɪkɪd">wicked</phoneme>'
    return combined_sentences_word_list

#This is the heteronym entry that makes the most assumptions on the meaning of the word "wind".
#It is assumed that the noun "wind" designates the movement of air, and not the act of winding or state of being wound, or a single turn/bend.
#As different forms of the verb "wind" may be pronounced differently, only the phoneme for "ˈwaɪnd" is substituted for "wind" in so far as "wind" is followed
#by "up". Caution is warranted here, as the other phoneme could be used before "up" as well.
def wind(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Wind" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i+1][0].lower() == "up":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈwaɪnd">Wind</phoneme>'
        elif combined_sentences_token_list[i][0] == "wind" and combined_sentences_token_list[i][1][:2] == "VB" and combined_sentences_token_list[i+1][0].lower() == "up":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈwaɪnd">wind</phoneme>'
        elif combined_sentences_token_list[i][0] == "Wind" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈwɪnd">Wind</phoneme>'
        elif combined_sentences_token_list[i][0] == "wind" and combined_sentences_token_list[i][1][:2] == "NN":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="ˈwɪnd">wind</phoneme>'
    return combined_sentences_word_list

#Spacy does not tokenize the following heteronym very accurately.
#You may need to replace the phome tag by its alternative form if the tokenization was wrong.
def wound(combined_sentences_word_list, combined_sentences_token_list):
    for i in range(len(combined_sentences_token_list)):
        if combined_sentences_token_list[i][0] == "Wound" and combined_sentences_token_list[i][1][:3] == "VBD":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="waʊnd">Wound</phoneme>'
        elif combined_sentences_token_list[i][0] == "wound" and combined_sentences_token_list[i][1][:3] == "VBD":
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="waʊnd">wound</phoneme>'
        elif combined_sentences_token_list[i][0] == "Wound" and combined_sentences_token_list[i][1][:2] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="wuːnd">Wound</phoneme>'
        elif combined_sentences_token_list[i][0] == "wound" and combined_sentences_token_list[i][1][:2] in ["VB", "NN"]:
            combined_sentences_word_list[i] = '<phoneme alphabet="ipa" ph="wuːnd">wound</phoneme>'
    return combined_sentences_word_list


#The "set_of_heteronyms_in_text" will be populated with the words in "combined_sentences_word_list" if they are present in either
#"heteronyms_list_American_English" or "heteronyms_list_American_English based"
set_of_heteronyms_in_text = set()
for word in combined_sentences_word_list:
    if English_Phonetics == "American_English" and word.capitalize() in heteronyms_list_American_English:
        set_of_heteronyms_in_text.add(word)
    elif English_Phonetics == "British_English" and word.capitalize() in heteronyms_list_British_English:
        set_of_heteronyms_in_text.add(word)

#This function appends spaces between elements of 'combined_sentences_word_list' if the last character of an element is alphabetic and the next element isn't "n't" (to prevent getting "do n't" instead of "don't", as Spacy tokenizes "don't" as "do" + "n't")
#and the first character of the next element is also alphabetic, or a bracket or starting quote sign (to avoid results such as 'word1(word2)'). It also appends spaces between elements of the list if the last character is not alphabetic, and the
#first character of the next element is alphabetic (to add a space after a comma, for example), but not if the first character of the next element is a bracket or a starting quote sign (to avoid
#results such as '( word'). Otherwise, it doesn't add any spaces.
def make_new_sentences(combined_sentences_word_list):
    combined_sentences_word_list_with_spaces = []
    for i in range(len(combined_sentences_word_list)-1):
        if combined_sentences_word_list[i][-1].isalpha() == True and combined_sentences_word_list[i+1]!= "n’t" and (combined_sentences_word_list[i+1][0].isalpha() == True or combined_sentences_word_list[i+1][0] in ['(', '[', '{', '“', "‘", "<"]):
            combined_sentences_word_list_with_spaces.append(combined_sentences_word_list[i])
            combined_sentences_word_list_with_spaces.append(" ")
        elif combined_sentences_word_list[i][-1].isalpha() == False and combined_sentences_word_list[i][-1] not in ['(', '[', '{', '“', "‘", "-"] and combined_sentences_word_list[i+1][0].isalpha() == True:
            combined_sentences_word_list_with_spaces.append(combined_sentences_word_list[i])
            combined_sentences_word_list_with_spaces.append(" ")
        else:
            combined_sentences_word_list_with_spaces.append(combined_sentences_word_list[i])
    combined_sentences_word_list_with_spaces.append(combined_sentences_word_list[-1])
    new_combined_sentences = "".join(combined_sentences_word_list_with_spaces)
    new_sentences = [sentence.strip() for sentence in re.split("===", new_combined_sentences) if sentence != '']
    return new_sentences

#Only pass 'text' and 'combined_sentences_token_list' in the heteronym functions if a heteronym was found in 'combined_sentences_word_list'
#If there are hyphens in the heteronym (ex: "co-ordinate"), they will be replaced with underscores (ex: "co_ordinate") for the function call.
sentence_index = 0
if len(set_of_heteronyms_in_text) > 0:
    for heteronym in set_of_heteronyms_in_text:
        #Since "import" is an internal python command, the function call needs to be different, hence the addition of "_heteronym"
        #to give the following function call: "import_heteronym(args)".
        if heteronym == "import":
            new_combined_sentences_word_list = eval(heteronym.lower() + "_heteronym")(combined_sentences_word_list, combined_sentences_token_list)
            new_sentences = make_new_sentences(new_combined_sentences_word_list)
        else:
            new_combined_sentences_word_list = eval(heteronym.lower())(combined_sentences_word_list, combined_sentences_token_list)
            new_sentences = make_new_sentences(new_combined_sentences_word_list)
    #Cycling through the "set_of_sentence_indices_with_heteronyms" to replace the original sentences in the whole text that contain heteronyms
    #with the corresponding "new_sentences" (after substitution of the SSML phoneme tags for the original heteronyms). Since the original sentence
    #indices come from a set, even if a sentence contains several different heteronyms, only one "index" will be used for the "whole_text.replace()"
    #methods per sentence containing heteronyms. Thus, the total number of sentences in the "set_of_sentence_indices_with_heteronyms" matches up with the
    #number of sentences in the "new_sentences".
    counter = 0
    for index in set_of_sentence_indices_with_heteronyms:
        sentences[index] = new_sentences[counter]
        counter+=1
#The updated sentences are joined without a space because the TTS rendition of acronyms would suffer from the addition of spaces in between the letters of the acronym.
#(The whole_text is split at "!", "?" or "." and the period could be part of an acronym such as "e.g." The absence of spaces in between new sentences and the previous
#punctuation mark does not seem to affect the TTS rendition in modern TTS websites.)
#A space is added after the punctuation mark if the length of the text following it is greater than one.
for i in range(len(sentences)-2):
    if sentences[i] not in ["!", "?", "\."] and len(sentences[i]) >= 1 and len(sentences[i+2]) > 1:
        sentences[i+2] = " " + sentences[i+2]
whole_text = "".join(sentences)

commas_semicolons_whole_text_after_modifications = whole_text.count(',') + whole_text.count(';')
#Calculating the relative percent increase in commas in the whole text after modifications.
if commas_semicolons_whole_text_before_modifications > 0:
    percent_increase_in_commas["Percent increase in commas in the whole text after modifications: "] = str(round((commas_semicolons_whole_text_after_modifications-commas_semicolons_whole_text_before_modifications)/commas_semicolons_whole_text_before_modifications*100)) + "%"
else:
    percent_increase_in_commas["Percent increase in commas in the whole text after modifications: "] = "There were no commas nor semicolons in the initial text and there are now " + str(commas_semicolons_whole_text_after_modifications) + " commas in the script after modifications."

#Selecting for potentially mispronounced capitalized words in whole_text who appear at least 4 times throughout the text.
for unknown_word in potentially_mispronounced_words:
    unknown_word_count = len(re.findall("[^\w]" + re.escape(unknown_word) + "[^\w]", whole_text))
    if unknown_word_count > 3 and len(unknown_word) > 1 :
        potentiallyMispronouncedWords_wordCounts[unknown_word] = unknown_word_count

#Calculating the "number_of_heteronym_substitutions" by subtracting the number of "<phoneme alphabet=" in the initial text from that of the final text.
final_phoneme_tag_count = whole_text.count("<phoneme alphabet=")
number_of_heteronym_substitutions = final_phoneme_tag_count-initial_phoneme_tag_count

#All of the data will be outputed in a single dictionary (entireData_dictionaries), whose sole key is mapped to a value consisting of a list of
#six dictionaries/lists/strings. The title of the individual dictionaries (sentencesManyCommas_sentenceIndex, sentencesFewCommas_sentenceIndex, potentiallyMispronouncedWords_wordCounts, percent_increase_in_commas) give insight as to the structure of the dictionaries: KeyNames_ValueName1ValueName2ValueName3.
entireData_dictionaries[0] = [sentencesManyCommas_sentenceIndex, sentencesFewCommas_sentenceIndex, potentiallyMispronouncedWords_wordCounts, percent_increase_in_commas, number_of_heteronym_substitutions, whole_text]

print(json.dumps(entireData_dictionaries, ensure_ascii=False))
