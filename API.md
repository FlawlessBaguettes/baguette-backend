# API 

## Posts

### Get Post

To get the data related to a single post

```http
GET /baguette/api/v1.0/posts/<post_id>
```

Where `post_id` is a UUID of a valid post

#### Success Reponse
*Code:* 200
If the post exists, then it will provide the following:

| Attribute        | Description           | Nullable?  |
| ------------- |-------------| -----|
| id      | Id of the post | False |
| parent_id      | Id of the immediate parent post      |   True |
| title | Title of the post     |  False |
| user | The user object      |    False |
| user.full_name | The full name of the user      |    False |
| user.first_name | The first name of the user      |    False |
| user.last_name | The last name of the user      |    False |
| user.username | The username of the user      |    False |
| user.user_id | The user Id of the user      |    False |
| content | The content object      |    False |
| content.url | The YouTube Url of the post      |    False |
| content.posted_time | The pretty date for the posted time      |    False |
| number_of_replies | The number of replies to the post    |    False |
| created_at | The time the post was created    |    False |
| updated_at | The time the post was last updated    |    True |

### Get Posts

To get all the top-level posts where `parent_id` is `null` 

```http
GET /baguette/api/v1.0/posts
```

#### Success Reponse
*Code:* 200

| Attribute        | Description           | Nullable?  |
| ------------- |-------------| -----|
| number_of_posts        | The number of posts returned          | False  |
| posts        | An array of `posts`          | False  |

### Get Post Replies

To get all the replies (immediate children) to a specific post

```http
GET /baguette/api/v1.0/posts/replies/<post_id>
```

Where `post_id` is a UUID of a valid post

#### Success Reponse
*Code:* 200

| Attribute        | Description           | Nullable?  |
| ------------- |-------------| -----|
| number_of_replies        | The number of replies for the post           | False  |
| replies        | An array of `posts`          | False  |

### Upload Post Video

*Note:* This is a temporary (WIP) endpoint 

To upload a video

```http
POST /baguette/api/v1.0/posts/upload
```

### Body
`video`: A mp4, mov, wmv, or avi file of maximum size of 10 MB

#### Success Reponse
*Code:* 201