(function() {
  var template = Handlebars.template, templates = Handlebars.templates = Handlebars.templates || {};
templates['search-results'] = template({"1":function(depth0,helpers,partials,data) {
  var helper, functionType="function", helperMissing=helpers.helperMissing, escapeExpression=this.escapeExpression;
  return "    <li class=\"result\">\n      <span class=\"name\">"
    + escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"name","hash":{},"data":data}) : helper)))
    + "</span><br/>\n      <span class=\"abv\">"
    + escapeExpression(((helper = (helper = helpers.abv || (depth0 != null ? depth0.abv : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"abv","hash":{},"data":data}) : helper)))
    + "</span>% – <span class=\"style\">"
    + escapeExpression(((helpers.style || (depth0 && depth0.style) || helperMissing).call(depth0, (depth0 != null ? depth0.style : depth0), {"name":"style","hash":{},"data":data})))
    + "</span><br/>\n      <span class=\"country\">"
    + escapeExpression(((helper = (helper = helpers.brewery_country || (depth0 != null ? depth0.brewery_country : depth0)) != null ? helper : helperMissing),(typeof helper === functionType ? helper.call(depth0, {"name":"brewery_country","hash":{},"data":data}) : helper)))
    + "</span>\n    </li>\n";
},"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
  var stack1, buffer = "<div id=\"search-results\">\n  <ol>\n";
  stack1 = helpers.each.call(depth0, (depth0 != null ? depth0.results : depth0), {"name":"each","hash":{},"fn":this.program(1, data),"inverse":this.noop,"data":data});
  if (stack1 != null) { buffer += stack1; }
  return buffer + "  </ol>\n</div>";
},"useData":true});
})();