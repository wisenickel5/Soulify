# Soulify
A 3rd Party Spotify Web Application that curates personalized playlists based on “preferred” user activity (ie. Liked Songs, Listening History, Hidden Songs) & gives users the access to a unique playlist creation tool that mixes music based on tunable attributes.

Vist https://soulify.herokuapp.com/ to use the Soulify Web App. **NOTE:** Because this application is still under development, individual users must be granted authorization. If you'd like access, please email me at dylanjalexander2@gmail.com and send your name along with your Spotify Username, or follow this MailTo link: https://mailxto.com/hd5ans

---

## Homepage

The spinning "Soulify" scene was created with [three.js library](https://threejs.org/). 

---

Frequent users of Spotify’s application are often disappointed by the “Daily Mix” Playlists that are created for all Spotify users. The Daily Mix Playlists area collection of songs that are either frequently played/liked by the user, or songs recommended by Spotify’s algorithm.

![image](https://user-images.githubusercontent.com/64096671/148821172-e9997d77-72be-4551-a943-738b5bf64825.png)

As an everyday Spotify user, I craved a tool that allowed me to easily create playlists with many songs at the touch of a button. After following either of the Top Tracks or Create links in the navigation bar, the user is prompted to enter their Spotify Credentials.

## Top Tracks

On this page, users are able to see they're most listened to songs over the last month, 6 months, and All Time.

![image](https://user-images.githubusercontent.com/64096671/148823189-5467beb8-8f38-4867-8d67-46333833787c.png)

Users are also able to see a radar chart that depicts the spread of their music taste! The chart is rendered after calling an Endpoint in the Spotify API that returns a user's liked songs; a Dataframe is then created with Pandas from the JSON retrieved. That dataframe is then normalized (a scaling technique that shifts & resizes values within the dataframe so that they are all between 0 - 1) and then extrapolated into the Radar Chart. The inspiration for a personalized visualization of liked songs came from this blog post: https://towardsdatascience.com/discovering-your-music-taste-with-python-and-spotify-api-b51b0d2744d

![image](https://user-images.githubusercontent.com/64096671/148823512-710f6a56-02fe-49cd-bb72-0fe468005eae.png)

## Create

The Create page gives users the ability to instantly create a playlist of 25 songs attuned to adjustable attributes the users sets after choosing a set of comparable songs and/or artists.

This screenshot shows the user choosing similar artists to model the playlist after:

![image](https://user-images.githubusercontent.com/64096671/148835711-37b18888-6de6-4668-9e4a-cc83894f0e96.png)

Adjusting the attributes: 

![image](https://user-images.githubusercontent.com/64096671/148835881-2b399f81-1281-411f-a517-260cac6ae8fc.png)

Our resulting playlist!

![image](https://user-images.githubusercontent.com/64096671/148835992-fdb9a4dc-5ca4-4723-b885-ebf3c21ca613.png)


