<!DOCTYPE html>
<html>
    <head>
        <%def name="title()"></%def>
        <title>${self.title()}</title>
        
        <meta name="viewport" content="width=device-width, initial-scale=1">
        
	<link   href="/static/styles/yui-3.5.0-cssreset-min.css"         rel="stylesheet"     />
        <link   href="/static/jquery.mobile/jquery.mobile-1.1.0.min.css" rel="stylesheet"     />
	<script src ="/static/scripts/jquery-1.7.2.min.js"                                     ></script>
	<script src ="/static/jquery.mobile/jquery.mobile-1.1.0.min.js"                        ></script>
        <link   href="/static/favicon.ico"                               rel="shortcut icon"  />
    </head>
    <body> 
        
        <div data-role="page">
                
            <div data-role="header" data-position="fixed" >
                <h1>KaraKara</h1>
                <a href="/" data-role="button" data-icon="home"   data-iconpos="left" >Home  </a>
                <a href="/" data-role="button" data-icon="search" data-iconpos="right">Search</a>
            </div><!-- /header -->
            
            <div data-role="content">
                ${next.body()}
            </div><!-- /content -->
        
        </div><!-- /page -->
        
    </body>
</html>