import cherrypy

cherrypy.config.update({'cherrypy.server.ssl_certificate' : 'cert.pem',
                        'cherrypy.server.ssl_private_key': 'privkey.pem'})