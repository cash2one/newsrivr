function clog(s) {
	console.log("== "+s+" ==")
}

function getHtmlDrops(drops, mobile) {	
	if (typeof mobile == "undefined") {
	  mobile = false;
	}	
    var template = "{{#drops}} \
<section class=\"post\" id=\"{{id_str}}\" style='opacity:1'> \
    <header> \
        <div class=\"frame\"> \
            <div class=\"bar\"> \
				<div class=\"block-tweeter\"> \
					<div class=\"ava\"> \
						{{#notretweeted}}\
						<img src=\"{{profile_image_url}}\" alt=\"\"> \
						{{/notretweeted}} \
						{{#retweeted}} \
						 <img src=\"{{retweet_profile_image_url}}\">\
						{{/retweeted}} \
					</div> \
					<div class=\"holder\"> \
						{{#notretweeted}}\
						<strong class=\"name\"><a target=\"_blank\" href='/{{screen_name}}'>{{name}}</a>&nbsp;<a href=\"http://twitter.com/#!/{{screen_name}}\" class=\"btn-bird\" target=\"_blank\"><!-- twitter --></a></strong> \
						<span class=\"meta\"><a target=\"_blank\" href=\"http://twitter.com/#!/{{screen_name}}/status/{{id_str}}\">{{timediff}}</a></span> \
						{{/notretweeted}}\
						{{#retweeted}}\
						<strong class=\"name\"><a target=\"_blank\" href='/{{retweet_screen_name}}'>{{retweet_name}}</a>&nbsp;<a href=\"http://twitter.com/#!/{{retweet_screen_name}}\" class=\"btn-bird\" target=\"_blank\"><!-- twitter --></a></strong> \
						<span class=\"meta\"><a target=\"_blank\" href=\"http://twitter.com/#!/{{retweet_screen_name}}/status/{{retweet_id_str}}\">{{retweet_timediff}}</a></span> \
						{{/retweeted}}\
					</div> \
				</div> \
				{{#retweeted}}\
				<div class=\"block-retweeter\"> \
					<div class=\"ava\"> \
						<img src=\"{{profile_image_url}}\" alt=\"\"> \
					</div> \
					<div class=\"holder\"> \
						<strong class=\"name\"><img src=\"/static/images/retweet.png\" alt=\"Retweeted\">by <a target=\"_blank\" href='/{{screen_name}}'>{{name}}</a>&nbsp;<a href=\"http://twitter.com/#!/{{screen_name}}\" class=\"btn-bird\" target=\"_blank\"><!-- twitter --></a>{{#retweet_count_available}}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(and <a target=\"_blank\" href=\"http://twitter.com/#!/{{retweet_screen_name}}/status/{{retweet_id_str}}\">{{retweet_count}} others</a>){{/retweet_count_available}}</strong> \
						<span class=\"meta\"><a target=\"_blank\" href=\"http://twitter.com/#!/{{screen_name}}/status/{{id_str}}\">{{timediff}}</a></span> \
					</div> \
				</div> \
				{{/retweeted}} \
            </div> \
            <div class=\"heading\"> \
                <h2>{{{org_content}}}</h2> \
            </div> \
			<div class=\"iconset\"> \
				<a onclick=\"javascript:replyDrop('{{id_str}}', '{{#retweeted}}{{retweet_id_str}}{{/retweeted}}{{#notretweeted}}{{id_str}}{{/notretweeted}}')\" class=\"btn-reply\" title=\"Reply\"><!-- reply --></a> \
				<a onclick=\"javascript:reTweetDialog('{{id_str}}', '{{#retweeted}}{{retweet_id_str}}{{/retweeted}}{{#notretweeted}}{{id_str}}{{/notretweeted}}')\" id='btn-retweet-{{id_str}}' class=\"btn-retweet-{{#isretweeted}}on{{/isretweeted}}{{#isnotretweeted}}off{{/isnotretweeted}}\" title=\"{{#isretweeted}}Undo retweet{{/isretweeted}}{{#isnotretweeted}}Retweet{{/isnotretweeted}}\"><!-- retweet --></a> \
				<a onclick=\"javascript:favoriteDrop('{{id_str}}', '{{#retweeted}}{{retweet_id_str}}{{/retweeted}}{{#notretweeted}}{{id_str}}{{/notretweeted}}')\" id='btn-favorite-{{id_str}}' class=\"btn-favorite-{{#isfavorite}}on{{/isfavorite}}{{#isnotfavorite}}off{{/isnotfavorite}}\" title=\"{{#isfavorite}}Unmark{{/isfavorite}}{{#isnotfavorite}}Mark{{/isnotfavorite}}&nbsp;as favorite\"><!-- favorite --></a> \
				<a onclick=\"javascript:shareDrop('{{_id}}', '{{id_str}}')\" class=\"btn-share\" title=\"Share\"><!-- share --><div id='tr1_{{id_str}}' rel=\"#shareoverlay\" class=\"toggleLayer\"></div></a> \
			</div> \
			{{#can_be_opened}} \
				<a onclick=\"javascript:openClose('{{_id}}', '{{id_str}}');\" id=\"oc_btn_{{id_str}}\" title=\"{{#post_closed}}Open all from {{name}}{{/post_closed}}{{#post_open}}Close all from {{name}}{{/post_open}}\" class=\"btn-open{{#post_closed}}-close{{/post_closed}}\"><!-- slide up/down --></a> \
			{{/can_be_opened}} \
        </div> \
    </header> \
    <article class=\"slide\"  id='slide_{{id_str}}' {{#cannot_be_opened}}style=\"display:none\"{{/cannot_be_opened}} {{#post_closed}}style=\"display:none;\"{{/post_closed}}> \
        <div class=\"frame\"> \
			{{#images}} \
				<div class=\"img-box\"> \
				<div class=\"img-holder\"><img src=\"{{src}}\" alt=\"\" width=\"{{width}}\" /></div> \
				<span class=\"top-l\">&nbsp;</span><span class=\"top-r\">&nbsp;</span><span class=\"bottom-l\">&nbsp;</span><span class=\"bottom-r\"></span> \
				</div> \
			{{/images}}	\
            {{#followed_links}} \
				{{#cinch}} \
					<audio src=\"{{mp3}}\" controls preload=\"auto\" autobuffer></audio><br/> \
					<a target='_blank' href='{{mp3}}'>direct link to mp3</a> \
				{{/cinch}} \
	            {{#youtube}} \
					{{#desc}} \
						<div class=\"clear\"><!-- --></div> \
							{{{desc}}} \
							<div class=\"img-box-youtube-main\"> \
							<div class=\"img-holder-youtube\"><object width='550' height='435'><param name=\"wmode\" value=\"transparent\"></param><param name='movie' value='http://www.youtube.com/v/{{videotag}}?fs=1&amp;hl=en_US'></param><param name='allowFullScreen' value='true'></param><param name='allowscriptaccess' value='always'></param><embed src='http://www.youtube.com/v/{{videotag}}?fs=1&amp;hl=en_US' type='application/x-shockwave-flash' allowscriptaccess='always' allowfullscreen='true' width='550' height='435' wmode='transparent'></embed></object> \</div> \
							<span class=\"top-l\">&nbsp;</span><span class=\"top-r\">&nbsp;</span><span class=\"bottom-l\">&nbsp;</span><span class=\"bottom-r\"></span> \
						</div> \
						{{#thumbs}} \
							<div class=\"img-box-youtube-thumb\"> \
							<div class=\"img-holder\"><img src=\"{{src}}\" alt=\"\" width=\"120\" height=\"90\" /></div> \
							<span class=\"top-l\">&nbsp;</span><span class=\"top-r\">&nbsp;</span><span class=\"bottom-l\">&nbsp;</span><span class=\"bottom-r\"></span> \
							</div><br /> \
						{{/thumbs}}  \
						<div class=\"clear\"><!-- --></div> \
					{{/desc}} \
				{{/youtube}} \
				{{#image}} \
					<div class=\"img-container\"> \
						<div class=\"img-box\"> \
							<div class=\"img-holder\"><img src=\"{{src}}\" alt=\"\" width=\"{{width}}\" /></div> \
							<span class=\"top-l\">&nbsp;</span><span class=\"top-r\">&nbsp;</span><span class=\"bottom-l\">&nbsp;</span><span class=\"bottom-r\"></span> \
						</div> \
					</div> \
				{{/image}} \
				{{#vimeo}} \
					{{{desc}}} \
					<div class=\"img-container\"> \
					<div class=\"img-box\"> \
						<div class=\"img-holder\" style=\"margin-bottom:-5px;\"><iframe src='{{iframe}}' width='706' height='450' frameborder='0'></iframe></div> \
						<span class=\"top-l\">&nbsp;</span><span class=\"top-r\">&nbsp;</span><span class=\"bottom-l\">&nbsp;</span><span class=\"bottom-r\"></span> \
					</div> \
					</div> \
				{{/vimeo}} \
				{{{simplehtml}}} \
				{{#adddivider}}<div class=\"divider\"><!-- --></div>{{/adddivider}} \
            {{/followed_links}} \
        </div> \
    </article>\
</section> \
{{/drops}}"        
    var html = Mustache.to_html(template, drops);
    return html;
}


