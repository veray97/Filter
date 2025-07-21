7/19/2025:

Cursor generated most of the code. But the code still need to be manually checked. It's not good enough. For example the PyQt5 always generate error messgaes, but it won't try PyQt6 until I told it to try. That's weird.

Example video need to be added to show the effect of filter. 

Try to add more filters, not only for human face, but for other objects, to increase applicability.

7/20/2025:

To compare the target face with the faces on screen, it use function **face_recognition.compare_faces** from the popular Python face_recognition library built on dlib’s facial recognition model

When I try the filter, I found that it's not ideal for Asian people's face comparison. So I search the internet and found that it indeed not ideal. In the github repository of dlib, I found a [closed but not solved issue](https://github.com/davisking/dlib/issues/1407) of the asian people face recognition. Maybe the solution for me is to [train the model](https://dlib.net/dnn_metric_learning_on_images_ex.cpp.html) with more dataset provided, or choose another model.
