
<!doctype html>
<html lang="en">
<head>
    <title>Cheer Up Your Buddy</title>
    <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.0.0/css/bootstrap.min.css">
</head>
<body>
    <ul id="friends" class="media-list">
    % for friend in friends:
        <li class="media">
        <a class="pull-left" href="https://www.facebook.com/{{ friend['uid'] }}">
        <img class="media-object" width="50" height="50" src="{{ friend['pic_square'] }}" />
        </a>
        <div class="media-body">
        <a class="media-heading" href="https://www.facebook.com/{{ friend['uid'] }}">{{ friend['name'] }}</a>
        <br/><span class="label label-primary">{{ friend['sentiment'] }}</span>
        </div>
        </li>
    % end
    </ul>
</body>
</html>