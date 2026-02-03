from .models import Post


class PostFactory:
    @staticmethod
    def create_post(author, content):
        return Post.objects.create(content=content, author=author)
