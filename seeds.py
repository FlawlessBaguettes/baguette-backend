from app import app, db
from datetime import date
from baguette_backend.models import content, post, user

# Create User
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
	print(str(e))

u = user.User.query.first()

# Create Content
try:
    c = content.Content(
        url = 'https://www.youtube.com/watch?v=CtmdUiv_sxs',
    )
    db.session.add(c)
    db.session.commit()
    print("Content added content id={}".format(c.id))
except Exception as e:
    db.session.rollback()
    print(str(e))

c = content.Content.query.first()


try:
    p = post.Post(
        parentId = None,
        contentId = c.id,
        userId = u.id,
    )
    db.session.add(p)
    db.session.commit()
    print("Post added post id={}".format(p.id))
except Exception as e:
    db.session.rollback()
    print(str(e))


