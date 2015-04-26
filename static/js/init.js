Handlebars.registerHelper('badge', function(rating) {
  var parts = (""+rating).split('.');
  if(parts[1] === undefined)
    parts[1] = "0";
  parts[1] = Math.ceil(parts[1]);
  // if(parts[0] === "0")
  //   return "★";
  // if(parts[0] === "1")
  //   return "★★";
  // if(parts[0] === "2")
  //   return "★★★";
  // if(parts[0] === "3")
  //   return "★★★★";
  // if(parts[0] === "4")
  //   return "★★★★★";
  if(parts[0] === "0")
    return "bad";
  if(parts[0] === "1")
    return "meh";
  if(parts[0] === "2")
    return "ok";
  if(parts[0] === "3")
    return "good";
  if(parts[0] === "4")
    return "great";
});

Handlebars.registerHelper('date', function(date){
  var months = "Jan_Feb_Mar_Apr_May_Jun_Jul_Aug_Sep_Oct_Nov_Dec".split("_");
  return months[parseInt(date.substring(5,7),10)-1]+", "+date.substring(0,4);
});


Handlebars.registerHelper('isStrong', function(abv, options) {
  if(this.abv >= 7.0) {
    return options.fn(this);
  }
});


Handlebars.registerHelper('style', function(style){
  if(style === 'Fruit Beer/Radler')
    return 'Fruit Beer';
  if(style === 'Spice/Herb/Vegetable')
    return 'Spice';
  if(style === 'Abt/Quadrupel')
    return 'Quadrupel';
  if(style === 'Sour Red/Brown')
    return 'Flanders Sour';
  if(style === 'Session IPA')
    return 'IPA';
  if(style === 'Imperial/Strong Porter')
    return 'Imperial Porter';
  if(style === 'Grodziskie/Gose/Lichtenhainer')
    return 'Gose';
  if(style === 'India Pale Ale (IPA)')
    return 'IPA';
  if(style === 'Sour/Wild Ale')
    return 'Sour';
  if(style === 'Imperial/Double IPA')
    return 'Double IPA';
  if(style === 'Strong Pale Lager/Imperial Pils')
    return 'Imperial Pils';
  if(style === 'Dunkel/Tmavý')
    return 'Dunkel';
  if(style === 'German Hefeweizen')
    return 'Hefeweizen';
  if(style === 'Belgian White (Witbier)')
    return 'Belgian White';
  if(style === 'Golden Ale/Blond Ale')
    return 'Golden Ale';
  else
    return style;
});