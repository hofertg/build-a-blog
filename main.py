#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

blogname = "Da blog"

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainHandler(Handler):
    def get(self):

        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")

        self.render('blogfront.html', maintitle=blogname, blogname=blogname, posts = posts)


class NewPostHandler(Handler):
    def get(self):
        self.render('newpost.html', maintitle="New Post", blogname=blogname, title="", blogcontent="", error="")

    def post(self):
        title = self.request.get("title")
        blogcontent = self.request.get("blogcontent")

        if title and blogcontent:
            post = BlogPost(title = title, content = blogcontent)
            post.put()

            self.redirect("/blog/" + str(post.key().id()))
        else:
            error = "We need both title and content!"
            self.render('newpost.html', blogname=blogname, title=title, blogcontent=blogcontent, error=error)


class ViewPostHandler(Handler):
    def get(self, id):
        post = BlogPost.get_by_id( int(id) )

        if not post:
            self.error(400)
            self.response.write("Oops! Something went wrong.")
            return

        self.render('blogfront.html', maintitle=post.title, blogname=blogname, posts = [post])





app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', MainHandler),
    ('/newpost', NewPostHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
