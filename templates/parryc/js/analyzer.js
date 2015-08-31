// Generated by CoffeeScript 1.6.3
var Analyzer,
  __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

Analyzer = (function() {
  function Analyzer(language) {
    var current, inflection, inflections, person, rule, schemaLength, verb, _i, _j, _len, _len1, _ref, _ref1;
    this.language = language;
    this.persons = ['1sg', '2sg', '3sg', '1pl', '2pl', '3pl'];
    this.inflectionEndings = [];
    this.inflections = (function() {
      var _results;
      _results = [];
      for (inflections in language.inflectionsRaw) {
        _results.push(inflections);
      }
      return _results;
    })();
    this.markers = language.markersRaw;
    _ref = this.inflections;
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      inflection = _ref[_i];
      verb = language.inflectionsRaw[inflection];
      schemaLength = verb.schema.length;
      this.inflectionEndings[inflection] = [];
      _ref1 = this.persons;
      for (_j = 0, _len1 = _ref1.length; _j < _len1; _j++) {
        person = _ref1[_j];
        this.inflectionEndings[inflection][person] = [];
        current = verb[person];
        if (!current['default']) {
          this.inflectionEndings[inflection][person] = this.replace(current, schemaLength);
        } else {
          for (rule in current) {
            this.inflectionEndings[inflection][person] = this.inflectionEndings[inflection][person].concat(this.replace(current[rule], schemaLength));
          }
        }
      }
    }
  }

  Analyzer.prototype.replace = function(sub, schemaLength) {
    var ending, key, letters, list, re, replacements, schemaPosition;
    list = [];
    replacements = sub['replacements'];
    schemaPosition = 0;
    while (schemaPosition < schemaLength) {
      ending = sub['form'];
      for (key in replacements) {
        letters = replacements[key];
        re = new RegExp(key, "gi");
        ending = ending.replace(re, letters[schemaPosition]);
      }
      list.push(ending.replace('+', '').replace('_', ' '));
      schemaPosition++;
    }
    return list.filter(function(value, index, self) {
      return self.indexOf(value) === index;
    });
  };

  Analyzer.prototype.getMorphology = function(word) {
    var potentials;
    potentials = this.getPerson(word);
    return this.getTense(potentials);
  };

  Analyzer.prototype.getPerson = function(word) {
    var currPers, ending, inflection, min, minRoot, person, potentialEnding, potentialRoot, results, uninflected, wordEnding, _i, _j, _k, _len, _len1, _len2, _ref, _ref1, _ref2;
    min = 0;
    currPers = "error";
    results = [];
    uninflected = [];
    _ref = this.inflections;
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      inflection = _ref[_i];
      _ref1 = this.persons;
      for (_j = 0, _len1 = _ref1.length; _j < _len1; _j++) {
        person = _ref1[_j];
        minRoot = 'superlongsuperlongomfgomfg';
        potentialEnding = '';
        _ref2 = this.inflectionEndings[inflection][person];
        for (_k = 0, _len2 = _ref2.length; _k < _len2; _k++) {
          ending = _ref2[_k];
          potentialRoot = word.substring(0, word.length - ending.length);
          wordEnding = word.substring(word.length - ending.length);
          if (wordEnding === ending && potentialRoot.length < minRoot.length) {
            minRoot = potentialRoot;
            potentialEnding = ending;
          }
        }
        if (ending.length !== 0 && minRoot !== 'superlongsuperlongomfgomfg') {
          results.push({
            'original': word,
            'person': person,
            'root': minRoot,
            'inflection': inflection,
            'hasMarkedInflection': true
          });
        } else {
          uninflected.push({
            'original': word,
            'person': person,
            'root': minRoot,
            'inflection': inflection,
            'hasMarkedInflection': false
          });
        }
      }
    }
    if (results.length === 0) {
      results = uninflected;
    }
    return results;
  };

  Analyzer.prototype.getTense = function(potentials) {
    var ambiguous, checkDerivation, derivations, exception, hasException, info, mark, marker, potential, result, resultList, root, rule, seenPairs, tense, _i, _len, _ref, _ref1, _ref2;
    result = {};
    resultList = [];
    seenPairs = [];
    ambiguous = false;
    hasException = false;
    for (_i = 0, _len = potentials.length; _i < _len; _i++) {
      potential = potentials[_i];
      tense = potential.inflection.split('-').pop();
      if (tense === 'VERB') {
        mark = '';
        tense = '';
      } else {
        mark = (_ref = this.language.inflections[potential.inflection].markers) != null ? _ref[0] : void 0;
      }
      marker = this.markers[mark];
      root = potential.root;
      if (marker != null) {
        for (rule in marker) {
          info = marker[rule];
          if (!(rule !== 'schema' && rule !== 'name')) {
            continue;
          }
          if (info.assimilation != null) {
            potential.root = this._unassimilate(info.assimilation, root);
          } else {
            potential.root = root.substring(0, root.length - info.form.length + 1);
          }
          checkDerivation = this.getDerivationalInformation(potential.root);
          potential.root = checkDerivation.root;
          derivations = checkDerivation.derivations;
          exception = this._getException(potential, tense);
          if (exception.valid) {
            potential = exception;
            tense = exception.tense;
            hasException = true;
          }
          if ((_ref1 = potential.root + "-" + tense, __indexOf.call(seenPairs, _ref1) < 0) && this.language.inflect(this.language.tempWord(potential.root, "VERB"), potential.person, tense, derivations) === potential.original) {
            resultList.push({
              'root': potential.root,
              'person': potential.person,
              'tense': tense,
              'derivations': derivations,
              'exception': false
            });
            seenPairs.push(potential.root + "-" + tense);
          }
        }
      } else {
        checkDerivation = this.getDerivationalInformation(potential.root);
        potential.root = checkDerivation.root;
        derivations = checkDerivation.derivations;
        exception = this._getException(potential, tense);
        if (exception.valid) {
          potential = exception;
          tense = exception.tense;
          hasException = true;
        }
        if ((_ref2 = potential.root + "-" + tense, __indexOf.call(seenPairs, _ref2) < 0) && this.language.inflect(this.language.tempWord(potential.root, "VERB"), potential.person, tense, derivations) === potential.original) {
          resultList.push({
            'root': potential.root,
            'person': potential.person,
            'tense': tense,
            'derivations': derivations,
            'exception': hasException
          });
          seenPairs.push(potential.root + "-" + tense);
        }
      }
    }
    if (resultList.length > 1) {
      ambiguous = true;
    }
    return {
      'ambiguous': ambiguous,
      'results': resultList
    };
  };

  Analyzer.prototype.getDerivationalInformation = function(root) {
    var derivation, derivationsList, endingLength, hasMatch, info, match, potentialRoot, re, replacement, replacements, rule, _i, _j, _len, _len1, _ref;
    derivationsList = [];
    potentialRoot = root;
    _ref = this.language.derivationsRaw.slice(0).reverse();
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      derivation = _ref[_i];
      for (rule in derivation) {
        info = derivation[rule];
        if (!(rule !== 'schema' && rule !== 'name' && rule !== 'order')) {
          continue;
        }
        replacements = this.replace(info, derivation.schema.length);
        hasMatch = false;
        endingLength = 0;
        for (_j = 0, _len1 = replacements.length; _j < _len1; _j++) {
          replacement = replacements[_j];
          re = new RegExp(replacement + "$", "gi");
          match = potentialRoot.match(re);
          if (match != null) {
            hasMatch = true;
            endingLength = match[0].length;
          }
        }
        if (hasMatch) {
          derivationsList.unshift(derivation.name);
          potentialRoot = potentialRoot.substring(0, potentialRoot.length - endingLength);
          if (info.assimilation != null) {
            potentialRoot = this._unassimilate(info.assimilation, potentialRoot);
          }
        }
      }
    }
    return {
      "root": potentialRoot,
      "derivations": derivationsList
    };
  };

  Analyzer.prototype._unassimilate = function(rules, word) {
    var end, rule, _i, _len;
    rules = rules.split(',').reverse();
    for (_i = 0, _len = rules.length; _i < _len; _i++) {
      rule = rules[_i];
      rule = rule.trim();
      rule.replace(/\+/gi, "");
      if (rule.indexOf('remove') === 0) {
        word = word + rule.slice("remove".length + 1);
      }
      if (rule.indexOf('double') === 0) {
        end = word.match(/(\w)(\1+)/g);
        if (end != null) {
          end = end.pop();
          word = word.replace(end, end.substring(end.length - 1));
        }
      }
    }
    return word.replace(/\s/gi, "").replace(/_/gi, " ");
  };

  Analyzer.prototype._getException = function(potential, tense) {
    var exception;
    if (this.language.exceptionMap[potential.original + '-' + tense] != null) {
      potential.root = potential.original;
    }
    exception = this.language.exceptionMap[potential.root + '-' + tense];
    if (potential.hasMarkedInflection) {
      exception = this.language.exceptionMap[potential.root + '+-' + tense];
    }
    if (exception != null) {
      potential.valid = true;
      potential.root = exception.root;
      potential.tense = tense;
      if (!potential.hasMarkedInflection) {
        potential.person = exception.person;
      }
    }
    return potential;
  };

  return Analyzer;

})();

if (typeof module !== 'undefined' && (module.exports != null)) {
  exports.Analyzer = Analyzer;
}