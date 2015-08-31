(function(window){
  window.hungarian = new Language("hungarian");

  hungarian = new Language("hungarian");

  hw = hungarian.words;

  hungarian.orthography({
    "vowels": {
      "all": "áóúőűéíaoueiöü",
      "back": "aáoóuú",
      "front": {
        "rounded": "öőüű",
        "unrounded": "eéií"
      },
      "long": "áóúőűéí",
      "short": "aoueiöü"
    },
    "consonants" : "bc(cs)d(dz)(dzs)fg(gy)hjkl(ly)mn(ny)prs(sz)t(ty)vz(zs)",
    "sibilants": "s(sz)z(dz)",
    "palatals": "jl(ly)n(ny)r"
  });

  hungarian.inflection({
    "word":"van",
    "VERB":{
      "1sg,1pl,2pl":"vagy+",
      "2sg":"vagy",
      "3sg":"van",
      "3pl":"van+"
    },
    "VERB-PST":{
      "1sg,3sg,1pl,2pl,3pl":"vol+",
      "2sg":"voltál"
    },
    "VERB-SUBJ":{
      "1sg,2sg,3sg,1pl,2pl,3pl":"legy+"
    },
    "VERB-COND":{
      "1sg,2sg,3sg,1pl,2pl,3pl":"vol+"
    }
  });

  hungarian.inflection({
    "schema": ["back","front.unrounded","front.rounded"],
    "name": "VERB",
    "preprocess": {"for":"2sg,1pl,2pl,3pl","do":"remove ik"},
    "1sg": {
      "default": {
        "form": "+Vk",
        "replacements": {
          "V": ["o", "e", "ö"]
        }
      },
      "-ik": {
        "form": "+Vm",
        "replacements": {
          "V": ["o", "e", "ö"]
        }
      }
    },
    "2sg": {
      "default": {
        "form":"+sz",
        "replacements":{"V":["a","e","e"]}
      },
      "after 'consonants' x2 or 'vowels.long' + t": {
        "form":"+Vsz",
        "replacements":{"V":["a","e","e"]}
      },
      "after 'sibilants'": {
        "form":"+Vl",
        "replacements":{"V":["o","e","ö"]}
      }
    },
    "3sg": {
      "form": "+",
      "replacements": {}
    },
    "1pl": {
      "form": "+Vnk",
      "replacements": {
        "V": ["u", "ü", "ü"]
      }
    },
    "2pl": {
      "default":{
        "form": "+tVk",
        "replacements": {"V": ["o", "e", "ö"]}
      },
      "after 'consonants' x2 or 'vowels.long' + t": {
        "form": "+VtVk",
        "replacements": {"V": ["o", "e", "ö"]}
      }
    },
    "3pl": {
      "default": {
        "form": "+nVk",
        "replacements": {"V": ["a", "e", "e"]}
      },
      "after 'consonants' x2 or 'vowels.long' + t": {
        "form": "+VnVk",
        "replacements": {"V": ["a", "e", "e"]}
      }
    }
  });


  hungarian.inflection({
    "schema": ["back","front"],
    "name": "VERB-PST",
    "markers": ["PST"],
    "preprocess": {"for":"all","do":"remove ik"},
    "1sg": {
      "form": "+Vm",
      "replacements": {"V": ["a","e"]}
    },
   "2sg": {
      "form": "+Vl",
      "replacements": {"V": ["ú","é"]}
    },
    "3sg": {
      "form": "+",
      "replacements": {}
    },
    "1pl": {
      "form": "+Vnk",
      "replacements": {"V": ["u","ü"]}
    },
    "2pl": {
      "form": "+AtBk",
      "replacements": {"A": ["a","e"], "B": ["o","e"]}
    },
    "3pl": {
      "form": "+Vk",
      "replacements": {"V": ["a","e"]}
    }
  });

  hungarian.inflection({
    "schema": ["back","front.unrounded","front.rounded"],
    "name": "VERB-SUBJ",
    "markers": ["SUBJ"],
    "1sg": {
      "form": "+Vk",
      "replacements": {"V": ["a","e","e"]}
    },
    "2sg": {
      "form": "+",
      "replacements": {}
    },
    "3sg": {
      "form": "+n",
      "replacements": {"V": ["o","e","ö"]}
    },
    "1pl": {
      "form": "+Vnk",
      "replacements": {"V": ["u","ü","ü"]}
    },
    "2pl": {
      "form": "+AtBk",
      "replacements": {"A": ["a","e","e"], "B": ["o","e","e"]}
    },
    "3pl": {
      "form": "+VnVk",
      "replacements": {"V": ["a","e","e"]}
    }
  });

  hungarian.inflection({
    "schema": ["back","front"],
    "name": "VERB-COND",
    "markers": ["COND"],
    "preprocess": {"for":"all","do":"remove ik"},
    "1sg": {
      "form": "+nék",
      "replacements": {}
    },
    "2sg": {
      "form": "+nVl",
      "replacements": {"V": ["á","é"]}
    },
    "3sg": {
      "form": "+nV",
      "replacements": {"V": ["a","e"]}
    },
    "1pl": {
      "form": "+nVnk",
      "replacements": {"V": ["á","é"]}
    },
    "2pl": {
      "form": "+nAtBk",
      "replacements": {"A":  ["á","é"], "B": ["o","e"]}
    },
    "3pl": {
      "form": "+nAnBk",
      "replacements": {"A":  ["á","é"], "B": ["a","e"]}
    }
  });

  hungarian.inflection({
    "schema": ["back","front"],
    "name": "VERB-FUT",
    "markers": ["INF"],
    "1sg": {
      "form": "_fogok",
      "replacements": {}
    },
    "2sg": {
      "form": "_fogsz",
      "replacements": {}
    },
    "3sg": {
      "form": "_fog",
      "replacements": {}
    },
    "1pl": {
      "form": "_fogunk",
      "replacements": {}
    },
    "2pl": {
      "form": "_fogtok",
      "replacements": {}
    },
    "3pl": {
      "form": "_fognak",
      "replacements": {}
    }
  });

  hungarian.marker({
    "schema": ["back", "front.unrounded", "front.rounded"],
    "name": "PST",
    "after 'consonants' x2 or 'vowels.long' + t": {
      "exceptions": ["fut","hat", "jut", "köt", "nyit", "süt", "üt", "vet"],
      "form": "+Vtt",
      "replacements": {"V": ["o","e","ö"]}
    },
    "after 'palatals' or +ad or +ed": {
      "exceptions": ["áll","száll","varr","forr"],
      "form": "+t",
      "replacements":{}
    },
    "default": {
      "exceptions": ["lát", "küld", "mond", "keyd", "függ", "fedd"],
      "overrides": {"3sg" :{
          "form": "+Vtt",
          "replacements": {"V": ["o","e","ö"]}
        }
      },
      "form": "+t",
      "replacements": {}
    }
  });

  hungarian.marker({
    "schema": [],
    "name": "SUBJ",
    "after 'sibilants'": {
      "assimilation": "double",
      "form":"+",
      "replacements":{}
    },
    "after (s|sz) + t": {
      "assimilation": "remove t, double",
      "form":"+",
      "replacements":{}
    },
    "after 'vowels.long' + t or 'consonants' + t":{
      "form":"+s",
      "replacements":{}
    },
    "after 'vowels.short' + t":{
      "assimilation": "remove t",
      "form":"+ss",
      "replacements":{}
    },
    "default": {
      "form":"+j",
      "replacements":{}
    }
  });

  //Rolled the actual marker into the inflection for ease of rules.
  //It's actually shown that way in Rounds' Hungarian Grammar, too. [4.3.7.1]
  hungarian.marker({
    "schema": ["back","front"],
    "name": "COND",
    "after 'vowels.long' + t or 'consonants' + t":{
      "exceptions":  ["áll","száll","varr","forr"],
      "form":"+V",
      "replacements":{"V":["a","e"]}
    },
    "default": {
      "form":"+",
      "replacements":{}
    }
  });

  hungarian.marker({
    "schema": ["back","front"],
    "name": "INF",
    "after 'vowels.long' + t or 'consonants' + t":{
      "exceptions":  ["áll","száll","varr","forr"],
      "form":"+Vni",
      "replacements":{"V":["a","e"]}
    },
    "default": {
      "form":"+ni",
      "replacements":{}
    }
  });

  /*************************
    Derivational Endings
   *************************/
  hungarian.marker({
    "schema": ["back", "front.unrounded", "front.rounded"],
    "name": "Frequentive",
    "order": 0,
    "only ('consonants')'vowels.all''consonants'":{
      "form":"+AgBt",
      "replacements":{
        "A": ["o","e","ö"],
        "B": ["a","e","e"]
      }
    },
    "default":{
      "form":"+gVt",
      "replacements":{"V":["a","e","e"]}
    }
  }, true);

  hungarian.marker({
    "schema": ["back","front"],
    "name": "Potential",
    "order": 1,
    "default":{
      "form":"+hVt",
      "replacements":{"V":["a","e"]}
    }
  }, true);

  //The Hungarian causative is not like the English causative, and is rarely used generally - mostly in well established verb pairs.
  //http://forum.wordreference.com/showthread.php?t=2148708
  //It also saves me the trouble of trying to figure out how to do syllable structure... 


  hungarian.phraseStructure("S","VERB");

  window.analyzer = new Analyzer(hungarian);
})(window);