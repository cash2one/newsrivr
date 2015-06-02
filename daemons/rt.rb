require 'rubygems'
require 'readability'
require 'open-uri'

source = open('http://scripting.com/stories/2011/01/23/aNewYorkVignette.html#disqus_thread').read
puts Readability::Document.new(source).content
