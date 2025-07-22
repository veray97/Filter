7/19/2025:

Start Point: Use Gemini to get the prompts. Manually modified a little. Then use Cursor to generate most of the code. But the code is not good enough. For example the PyQt5 always generate error messgaes, but it won't try PyQt6 until I told it to try. That's weird. 

> The algorithm of the code generated to realize theis to:
>> 1. take screenshots of the area below the pop-up window.
>> 2. use model to recognize the face and compare with target face
>> 3. if target face is detected, add a blur to the screenshot 
>> 4. display the updated screenshots in the pop-up window

> The primary challenge with this algorithm is the latency introduced in video playback. My initial idea was to take more screenshots to create the video, instead of frequently cutting frames since each page appears individually. Another approach was to use a GPU to speed up the face recognition model and compare it with the target face. However this will take more time to develop. One thing that is close to my life is zoom or tiktok, which all have function of filter. Why is it so easy to apply the filter on camera. Then I came up with my answer for this question. The filter is only added on face, which means the other parts are all "transparent"! The face on the camera will not move as fast as spaceship. So even though there is delay to take screenshots and then analyze it and then add filter on the video, the filtered area, which is the face area, will not move too much away from the filter. So it's difficult to tell if there is delay. (And large company will also use GPU, which will also eliminate latency)

Example video need to be added to show the effect of filter. 

Try to add more filters, not only for human face, but for other objects, to increase applicability.

7/20/2025:

To compare the target face with the faces on screen, it use function **face_recognition.compare_faces** from the popular Python face_recognition library built on dlib’s facial recognition model

When I try the filter, I found that it's not ideal for Asian people's face comparison. So I search the internet and found that it indeed not ideal. In the github repository of dlib, I found a [closed but not solved issue](https://github.com/davisking/dlib/issues/1407) of the asian people face recognition. Maybe the solution for me is to [train the model](https://dlib.net/dnn_metric_learning_on_images_ex.cpp.html) with more dataset provided, or choose another model.
