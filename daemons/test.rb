
require '/home/rabshakeh/Newsrivr/daemons/zreadability'
#require 'readability'

#text = open(ARGV.first).read
t1 ="usedforscoring.html"

p Readability::Document.new(File.open(t1).read()).content
