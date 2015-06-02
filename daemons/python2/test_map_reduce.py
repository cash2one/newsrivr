from __future__ import print_function
from builtins import str

from d_utils import *
from pymongo.code import Code
import calendar

def getTimeWithMS2():
	dtn = datetime.datetime.utcnow()
	before = str(calendar.timegm(dtn.timetuple()))
	after = repr(time.time())
	sa = after.split(".")
	dtnms = dtn
	if len(sa)>1:
		dtnms = before + "." + sa[1]
	return dtn, float(dtnms)

def main():

    wordmap = """
function wordMap(){
	//find words in the document text
	var words = this.org_content.match(/\w+/g);	
	if (words == null){
		return;
	}	
	for (var i = 0; i < words.length; i++){
		//emit every word, with count of one
		emit(words[i], {count: 1});	
	}
}"""
    
    wordreduce = """
function wordReduce(key,values){
	var total = 0;
	for (var i = 0; i < values.length; i++){
		total += values[i].count;
	}
	return {count: total};
}"""

    #Load map and reduce functions
    map = Code(wordmap)
    reduce = Code(wordreduce)
    
    db = getDB()
    coll = db.drops
    
    #Run the map-reduce query
    result = "wordcount"
    results = coll.map_reduce(map,reduce, result, query={"name": "Integron"})
    
    #Print the results
    for result in results.find():
        print(result['_id'] , result['value']['count'])
    
#while True:
#	dtms = getTimeWithMS2()
#	print dtms
#	#time.sleep(0.5)
#	os.system("clear")
	


if __name__=="__main__":
    main()