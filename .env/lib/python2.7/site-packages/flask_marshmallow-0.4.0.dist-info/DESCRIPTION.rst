Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
Description: *****************
        Flask-Marshmallow
        *****************
        
        .. image:: https://badge.fury.io/py/flask-marshmallow.png
            :target: http://badge.fury.io/py/flask-marshmallow
            :alt: Latest version
        
        .. image:: https://travis-ci.org/sloria/flask-marshmallow.png?branch=master
            :target: https://travis-ci.org/sloria/flask-marshmallow
        
        
        Flask + marshmallow for beautiful APIs
        ======================================
        
        Flask-Marshmallow is a thin integration layer for `Flask`_ (a Python web framework) and `marshmallow`_ (an object serialization/deserialization library) that adds additional features to marshmallow, including URL and Hyperlinks fields for HATEOAS-ready APIs.
        
        
        Create your app.
        
        .. code-block:: python
        
            from flask import Flask, jsonify
            from flask.ext.marshmallow import Marshmallow
        
            app = Flask(__name__)
            ma = Marshmallow(app)
        
        Write your models.
        
        .. code-block:: python
        
            from your_orm import Model, Column, Integer, String, DateTime
        
            class User(Model):
                email = Column(String)
                password = Column(String)
                date_created = Column(DateTime, auto_now_add=True)
        
        
        Define your output format with marshmallow.
        
        .. code-block:: python
        
        
            class UserSchema(ma.Schema):
                class Meta:
                    # Fields to expose
                    fields = ('email', 'date_created', '_links')
                # Smart hyperlinking
                _links = ma.Hyperlinks({
                    'self': ma.URLFor('author_detail', id='<id>'),
                    'collection': ma.URLFor('authors')
                })
        
            user_schema = UserSchema()
            users_schema = UserSchema(many=True)
        
        
        Output the data in your views.
        
        .. code-block:: python
        
            @app.route('/api/users/')
            def users():
                all_users = User.all()
                result = users_schema.dump(all_users)
                return jsonify(result.data)
        
            @app.route('/api/users/<id>')
            def user_detail(id):
                user = User.get(id)
                result = user_schema.dump(user)
                return jsonify(result.data)
            # {
            #     "email": "fred@queen.com",
            #     "date_created": "Fri, 25 Apr 2014 06:02:56 -0000",
            #     "_links": {
            #         "self": "/api/authors/42",
            #         "collection": "/api/authors/"
            #     }
            # }
        
        
        Learn More
        ==========
        
        To learn more about marshmallow, check out its `docs <http://marshmallow.readthedocs.org/en/latest/>`_.
        
        
        Get it now
        ==========
        
        ::
        
            pip install flask-marshmallow
        
        
        http://flask-marshmallow.readthedocs.org/
        =========================================
        
        License
        =======
        
        MIT licensed. See the bundled `LICENSE <https://github.com/sloria/flask-marshmallow/blob/master/LICENSE>`_ file for more details.
        
        
        .. _Flask: http://flask.pocoo.org
        .. _marshmallow: http://marshmallow.readthedocs.org
        
        
        
        Changelog
        =========
        
        0.4.0 (2014-12-22)
        ******************
        
        * *Backwards-incompatible*: Rename ``URL`` and ``AbsoluteURL`` to ``URLFor`` and ``AbsoluteURLFor``, respectively, to prevent overriding marshmallow's ``URL`` field. Thanks @svenstaro for the suggestion.
        * Fix bug that raised an error when deserializing ``Hyperlinks`` and ``URL`` fields. Thanks @raj-kesavan for reporting.
        
        Deprecation:
        
        * ``Schema.jsonify`` is deprecated. Use ``flask.jsonify`` on the result of ``Schema.dump`` instead.
        * The ``MARSHMALLOW_DATEFORMAT`` and ``MARSHMALLOW_STRICT`` config values are deprecated. Use a base ``Schema`` class instead.
        
        0.3.0 (2014-10-19)
        ******************
        
        * Supports marshmallow >= 1.0.0-a.
        
        0.2.0 (2014-05-12)
        ******************
        
        * Implementation as a proper class-based Flask extension.
        * Serializer and fields classes are available from the ``Marshmallow`` object.
        
        0.1.0 (2014-04-25)
        ******************
        
        * First release.
        * ``Hyperlinks``, ``URL``, and ``AbsoluteURL`` fields implemented.
        * ``Serializer#jsonify`` implemented.
        
Keywords: flask-marshmallow
Platform: UNKNOWN
Classifier: Development Status :: 2 - Pre-Alpha
Classifier: Environment :: Web Environment
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Natural Language :: English
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.3
Classifier: Topic :: Internet :: WWW/HTTP :: Dynamic Content
