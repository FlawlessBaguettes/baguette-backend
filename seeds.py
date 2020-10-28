from app import app, db
from datetime import date
from app.models import content, post, user

# Create Users
u = None
try: 
	u = user.User(
			username = 'johndoe',
	        password = '12345',
	        email = 'johndoe@gmail.com',
	        first_name = 'John',
	        last_name = 'Doe',
	        date_of_birth = date(1990, 1, 1)
		)
	db.session.add(u)
	db.session.commit()
	print("User added user id={}".format(u.id))
except Exception as e:
    db.session.rollback()
    u = user.User.query.first()
    print(str(e))

u2 = None
try: 
    u2 = user.User(
            username = 'janedoe',
            password = '12345',
            email = 'janedoe@gmail.com',
            first_name = 'Jane',
            last_name = 'Doe',
            date_of_birth = date(1991, 1, 1)
        )
    db.session.add(u2)
    db.session.commit()
    print("User added user id={}".format(u2.id))
except Exception as e:
    db.session.rollback()
    u2 = user.User.query.first()
    print(str(e))


# Create Content
c = None
try:
    c = content.Content(
        url = 'https://www.youtube.com/watch?v=CtmdUiv_sxs',
    )
    db.session.add(c)
    db.session.commit()
    print("Content added content id={}".format(c.id))
except Exception as e:
    db.session.rollback()
    c = content.Content.query.first()
    print(str(e))

c2 = None
try:
    c2 = content.Content(
        url = 'https://www.youtube.com/watch?v=BGrfhsxxmdE',
    )
    db.session.add(c2)
    db.session.commit()
    print("Content added content id={}".format(c2.id))
except Exception as e:
    db.session.rollback()
    c2 = content.Content.query.first()
    print(str(e))


# Create Parent Posts
p = None
try:
    p = post.Post(
        parentId = None,
        contentId = c.id,
        userId = u.id,
        title = u.first_name + " " + u.last_name + "'s parent post"
    )
    db.session.add(p)
    db.session.commit()
    print("Post added post id={}".format(p.id))
except Exception as e:
    db.session.rollback()
    p = post.Post.query.first()
    print(str(e))

p2 = None
try:
    p2 = post.Post(
        parentId = None,
        contentId = c2.id,
        userId = u2.id,
        title = u2.first_name + " " + u2.last_name + "'s parent post"
    )
    db.session.add(p2)
    db.session.commit()
    print("Post added post id={}".format(p2.id))
except Exception as e:
    db.session.rollback()
    p2 = post.Post.query.first()
    print(str(e))

# Create Child Posts
pc_1 = None
for i in range(5):
    try:
        pc_1 = post.Post(
            parentId = p.id,
            contentId = c.id,
            userId = u.id,
            title = u.first_name + " " + u.last_name + "'s child post " + str(i)
        )
        db.session.add(pc_1)
        db.session.commit()
        print("Post added post id={}".format(pc_1.id))
    except Exception as e:
        db.session.rollback()
        pc_1 = post.Post.query.filter(post.Post.parentId == p.id).first()
        print(str(e))

for i in range(5):
    try:
        pc_2 = post.Post(
            parentId = p2.id,
            contentId = c2.id,
            userId = u2.id,
            title = u2.first_name + " " + u2.last_name + "'s child post " + str(i)
        )
        db.session.add(pc_2)
        db.session.commit()
        print("Post added post id={}".format(pc_2.id))
    except Exception as e:
        db.session.rollback()
        print(str(e))

# Create Grandchild Posts
pgc_1 = None
for i in range(5):
    try:
        pgc_1 = post.Post(
            parentId = pc_1.id,
            contentId = c.id,
            userId = u.id,
            title = u.first_name + " " + u.last_name + "'s grandchild post " + str(i)
        )
        db.session.add(pgc_1)
        db.session.commit()
        print("Post added post id={}".format(pgc_1.id))
    except Exception as e:
        db.session.rollback()
        print(str(e))
