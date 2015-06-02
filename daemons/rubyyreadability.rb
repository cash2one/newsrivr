
require '/home/rabshakeh/Newsrivr/daemons/yreadability'

#text = open(ARGV.first).read
t1 = ARGV[0]
t2 = ARGV[1]

myfile = File.open(t2, "w+")
myfile.puts(Readability::Document.new(File.open(t1).read()).content)
