Using the application
---------------------

agoras publish
~~~~~~~~~~~~~~

This command allows you to publish a post in different social network.::

    $ agoras publish --help
    usage: agoras publish [options]

    General Options:
      -V, --version         Print version and exit.
      -h, --help            Show this help message and exit.

    Publish Options:
      -l <level>, --loglevel <level>
                            Logger verbosity level (default: INFO). Must be one of: DEBUG, INFO, WARNING, ERROR or CRITICAL.
      -n <social network>, --network <social network>
                            Social network to use for publishing (default: ""). Must be one of: twitter, facebook, instagram or linkedin.
      -a <action>, --action <action>
                            Action to execute (default: ""). Must be one of: like, share, last-from-feed, random-from-feed, schedule, post, delete
      -tk <consumer key>, --twitter-consumer-key <consumer key>
                            Twitter consumer key from twitter developer app.
      -ts <consumer secret>, --twitter-consumer-secret <consumer secret>
                            Twitter consumer secret from twitter developer app.
      -tot <oauth token>, --twitter-oauth-token <oauth token>
                            Twitter OAuth token from twitter developer app.
      -tos <oauth secret>, --twitter-oauth-secret <oauth secret>
                            Twitter OAuth secret from twitter developer app.
      -ti <id>, --tweet-id <id>
                            Twitter post ID to like, retweet or delete.
      -ft <access token>, --facebook-access-token <access token>
                            Facebook access token from facebook app.
      -fo <id>, --facebook-object-id <id>
                            Facebook ID of object where the post is going to be published.
      -fp <id>, --facebook-post-id <id>
                            Facebook ID of post to be liked, shared or deleted.
      -fr <id>, --facebook-profile-id <id>
                            Facebook ID of profile where a post will be shared.
      -it <access token>, --instagram-access-token <access token>
                            Facebook access token from facebook app.
      -io <id>, --instagram-object-id <id>
                            Instagram ID of profile where the post is going to be published.
      -ip <id>, --instagram-post-id <id>
                            Instagram ID of post to be liked, shared or deleted.
      -lw <access token>, --linkedin-access-token <access token>
                            Your LinkedIn access token.
      -lp <id>, --linkedin-post-id <id>
                            LinkedIn post ID to like, retweet or delete.
      -st <text>, --status-text <text>
                            Text to be published.
      -sl <link>, --status-link <link>
                            Link to be published.
      -i1 <image url>, --status-image-url-1 <image url>
                            First image URL to be published.
      -i2 <image url>, --status-image-url-2 <image url>
                            Second image URL to be published.
      -i3 <image url>, --status-image-url-3 <image url>
                            Third image URL to be published.
      -i4 <image url>, --status-image-url-4 <image url>
                            Fourth image URL to be published.
      -fu <feed url>, --feed-url <feed url>
                            URL of public Atom feed to be parsed.
      -mc <number>, --max-count <number>
                            Max number of new posts to be published at once.
      -pl <seconds>, --post-lookback <seconds>
                            Only allow posts published
      -ma <days>, --max-post-age <days>
                            Dont allow publishing of posts older than this number of days.
      -ge <email>, --google-sheets-client-email <email>
                            A google console project client email corresponding to the private key.
      -gk <private key>, --google-sheets-private-key <private key>
                            A google console project private key.
      -gi <id>, --google-sheets-id <id>
                            The google sheets ID to read schedule entries.
      -gn <name>, --google-sheets-name <name>
                            The name of the sheet where the schedule is.


Examples of usage
~~~~~~~~~~~~~~~~~

- :doc:`Using Agoras with Twitter <twitter>`
- :doc:`Using Agoras with Facebook <facebook>`
- :doc:`Using Agoras with Instagram <instagram>`
- :doc:`Using Agoras with LinkedIn <linkedin>`


Credentials
~~~~~~~~~~~

- :doc:`How to get credentials for Twitter <credentials/twitter>`
- :doc:`How to get credentials for Facebook <credentials/facebook>`
- :doc:`How to get credentials for Instagram <credentials/instagram>`
- :doc:`How to get credentials for LinkedIn <credentials/linkedin>`
- :doc:`How to get credentials for Google spreadsheets <credentials/google>`
