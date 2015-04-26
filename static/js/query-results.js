(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['query-results'] = template({"1":function(depth0,helpers,partials,data) {
  var stack1, helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression, buffer = "        <tr>\n          <td style=\"font-size: 1.7em;\">\n            <span class=\"beer-name\">"
    + escapeExpression(((helper = (helper = helpers.brewery || (depth0 != null ? depth0.brewery : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"brewery","hash":{},"data":data}) : helper)))
    + " "
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "</span><br/>\n            <span class=\"badge "
    + escapeExpression(((helpers.badge || (depth0 && depth0.badge) || helperMissing).call(depth0, (depth0 != null ? depth0.rating : depth0), {"name":"badge","hash":{},"data":data})))
    + " rating\"></span>\n            <span class=\"flag-icon flag-icon-"
    + escapeExpression(((helper = (helper = helpers.country_iso || (depth0 != null ? depth0.country_iso : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"country_iso","hash":{},"data":data}) : helper)))
    + " flag-icon-squared\"></span>\n";
  stack1 = ((helpers.isStrong || (depth0 && depth0.isStrong) || helperMissing).call(depth0, (depth0 != null ? depth0.abv : depth0), {"name":"isStrong","hash":{},"fn":this.program(2, data),"inverse":this.noop,"data":data}));
  if (stack1 != null) { buffer += stack1; }
  return buffer + "          </td>\n        </tr>\n";
},"2":function(depth0,helpers,partials,data) {
  return "              <i class=\"strong-beer fa fa-exclamation-circle\"></i> <span class=\"strong-beer-label\">High ABV</span>\n";
  },"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, buffer = "<div class=\"row\">\n  <table style=\"margin: 0 auto;\">\n    <thead></thead>\n    <tbody>\n";
  stack1 = helpers.each.call(depth0, (depth0 != null ? depth0.results : depth0), {"name":"each","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "    </tbody>\n  </table>\n</div>";
},"useData":true});
})();