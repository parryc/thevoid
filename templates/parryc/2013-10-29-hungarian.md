<!-- layout: post
categories: 
- creations
- languages
title: Hungarian
date: 2013-10-29
js: [aistritheoir, analyzer, hungarian, hungarian-page]
-->
#Hungarian
<tag>creations</tag> <tag>languages</tag> \\ 2013-10-29


Hungarian is a pretty cool language. It's aggluntinating, which means you add person, tense, and all other sorts of markers directly to the stem of the verb. I'll be using this page, and others, to chronicle my quest to learn Hungarian. Below, you'll find two tools I've created to help me on my way: an inflector and an analyzer.  The inflector takes the root form (also called a lemma or dictionary form) of a verb and inflects it correctly. It assumes the word you're inputting is Hungarian and applies rules according to the word's character. The inflector does the opposite - put in a word you think is a Hungarian verb, click inflect, and hope it gives you something useful. Because of certain problems in naïvely doing morphological inflections, there will occasionally be ambiguous results.

<!-- more -->


##The Inflector##

<div class="center">
	<select id="person" class="wide whitespace-vert">
		<option value="1sg">1st person singular</option>
		<option value="2sg">2nd person singular</option>
		<option value="3sg">3rd person singular</option>
		<option value="1pl">1st person plural</option>
		<option value="2pl">2nd person plural</option>
		<option value="3pl">3rd person plural</option>
	</select>
	<br/>
	<select id="tense" class="wide whitespace-vert">
		<option value="">Present</option>
		<option value="PST">Past</option>
		<option value="COND">Conditional</option>
		<option value="FUT">Future</option>
		<option value="SUBJ">Subjunctive</option>
	</select>
	<br/>
	<div class="inflect">
		<input id="word" type="text" placeholder="Verb" value="ért" class="wide whitespace-vert"/>
		<span id="answer">Inflection</span>
	</div>
	<button id="inflect">Inflect</button>
</div>

##The Analyzer##

<div class="center">
	<div class="analyze">
		<input id="unknown" type="text" placeholder="Verb" value="főzöl" class="wide whitespace-vert"/>
		<br/>
		<span id="analysis">Analysis</span>
	</div>
	<button id="analyze">Analyze</button>
</div>


<blockquote>With insurmountable help from <em>Hungarian: an Essential Grammar</em> by Carol H. Rounds</blockquote>

