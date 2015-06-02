
import os
import pickle
import urlparse
from oauthtwitter import OAuthApi
from dateutil.parser import parse

consumer_key = "sRXKCWePy0kG43DwiG9kw"
consumer_secret = "ikO6z1CVFW4tv4NmpNo8QbhCHMQNjOq1Z7vWc25wA"

def main():
    access_token = dict(urlparse.parse_qsl("oauth_token_secret=XwWBUDkHnaswXueyaKVBEe9m49iuIUWYx9fqGZKIG4&oauth_token=223480661-ZT7pgB8X5E8ez3DEvcIT2B66o9T8rQPKMbvqlYiY"))
    twitter = OAuthApi(consumer_key, consumer_secret, access_token["oauth_token"], access_token["oauth_token_secret"])
    
    #print twitter.GetHomeTimeline({"count":200})
    scoble = eval(open("scoble.json", "r").read())
    print "len:", len(scoble)
    done = []
    for i in range(0,  len(scoble)):
        id = scoble[len(scoble)-1-i]
        
        print twitter.FollowUser(str(id))
        done.append(id)
        #print id
    open("done.p","w").write(pickle.dumps(done))
    
if __name__=="__main__":
    main()
    
"""
10202
1186
11334
2172
13341
11628
885
1317
13479
5699
414
12773
13352
10365
3936
1081
36823
25663
12514
649
10178
1378
47083
12217
1075
2691
57203
25583
65233
75493
257
79543
550943
511283
691353
791258
49793
10450
11414
792563
10997
754613
759186
7083
732773
332163
13098
67923
75533
723013
746323
229523
666773
48443
61233
12916
1192
755165
10326
11426
782310
778057
717313
10297
766347
404133
611953
186193
11900
633293
676203
11489
747
732873
12522
412503
679303
160763
45993
687363
755452
662773
673483
66393
608993
10221
3968
10336
611043
11525
46023
13545
754969
776197
64743
43553
796135
636843
26743
40153
620863
813491
767396
662433
806975
13669
754556
47333
623133
807360
649713
785637
771621
711303
816234
813887
624683
147093
125033
45773
13696
815106
720503
652193
"""    