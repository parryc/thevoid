var h = window.hungarian,
	a = window.analyzer,
	inflect = function(){
		var word = document.getElementById("word").value,
			tense = document.getElementById("tense").value,
			person = document.getElementById("person").value,
			answer = document.getElementById("answer"),
			button = document.getElementById("inflect"),
			verb;
		if(h.words[word] === undefined)
			h.word(word,"VERB");
		verb = h.words[word];

		answer.innerHTML = h.inflect(verb,person,tense);
		button.blur();
	},
	analyze = function(){
		var word = document.getElementById('unknown').value,
			analysis = document.getElementById('analysis');

		analysis.innerHTML = "";
		analyses = a.getMorphology(word);

		if(analyses.results.length > 0) {
			analyses.results.forEach(function(v,i){
				if(v.tense === "")
					v.tense = "PRES";

				analysis.innerHTML += v.root + " (" + v.person + "." + v.tense + ")";
				for (var j = 0, l = v.derivations.length; j < l; j++) {
					analysis.innerHTML += " "+v.derivations[j];
					if(j < l-1)
						analysis.innerHTML += ",";
				}

				if(v.exception)
					analysis.innerHTML += " - is an exception";

				analysis.innerHTML += "<br/>";
			});
		} else {
			analysis.innerHTML = "There are no valid analyses.";
		}

	},
	inflectButton = document.getElementById("inflect"),
	analyzeButton = document.getElementById("analyze");


inflectButton.addEventListener("click",inflect);
analyzeButton.addEventListener("click",analyze);