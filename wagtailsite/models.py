from datetime import date

from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.management import call_command
from django.dispatch import receiver
from django.shortcuts import render
from django.http import HttpResponse

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel, PageChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailimages.models import Image
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsnippets.models import register_snippet


from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase

COMMON_PANELS = (
    FieldPanel('slug'),
    FieldPanel('seo_title'),
    FieldPanel('show_in_menus'),
    FieldPanel('search_description'),
)


#  == Snippet:Author ==

class AuthorSnippet(models.Model):
    title = models.CharField(max_length=255, help_text='This is the reference name for the contact. This is not displayed on the frontend.')
    author_name = models.CharField(max_length=255)
    author_title = models.CharField(max_length=255, blank=True)
    author_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    author_biog = models.TextField(blank=True, help_text='A short description of the author')
    author_link = models.URLField(blank=True)
    author_link_text = models.CharField(max_length=255, blank=True)
    author_twitter = models.URLField(blank=True, help_text='Enter a twitter address')
    author_twitter_text = models.CharField(max_length=255, blank=True, help_text='Enter a twitter handle')

    def __unicode__(self):
        return self.title

AuthorSnippet.panels = [
    FieldPanel('title'),
    FieldPanel('author_name'),
    FieldPanel('author_title'),
    ImageChooserPanel('author_image'),
    FieldPanel('author_biog'),
    FieldPanel('author_link'),
    FieldPanel('author_link_text'),
    FieldPanel('author_twitter'),
    FieldPanel('author_twitter_text'),
]

register_snippet(AuthorSnippet)


class AuthorSnippetPlacement(models.Model):
    page = ParentalKey(Page, related_name='author_snippet_placements')
    author_snippet = models.ForeignKey('wagtailsite.AuthorSnippet', related_name='+')


#  == Related links ==

class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True


class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


#  == Homepage ==


class HomePage(Page):
    search_name = "Homepage"

    class Meta:
        verbose_name = "Homepage"

HomePage.content_panels = [
    FieldPanel('title', classname="full title"),
]

HomePage.promote_panels = [
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
]


#  == Blog index ==

class BlogIndexPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('wagtailsite.BlogIndexPage', related_name='related_links')


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    indexed_fields = ('intro', )
    search_name = "Blog"

    @property
    def blogs(self):
        # Get list of blog pages that are descendants of this page
        blogs = BlogPage.objects.filter(
            live=True,
            path__startswith=self.path
        )

        # Order by most recent date first
        blogs = blogs.order_by('-date')

        return blogs

    def serve(self, request):
        # Get blogs
        blogs = self.blogs

        # Filter by tag
        tag = request.GET.get('tag')
        if tag:
            blogs = blogs.filter(tags__name=tag)

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(blogs, 5)  # Show 5 blogs per page
        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        return render(request, self.template, {
            'self': self,
            'blogs': blogs,
        })

BlogIndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel(BlogIndexPage, 'related_links', label="Related links"),
]

BlogIndexPage.promote_panels = [
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
]


#  == Blog page ==

class BlogPageAuthorSnippet(Orderable):
    page = ParentalKey('wagtailsite.BlogPage', related_name='author_snippets')
    author_snippet = models.ForeignKey('wagtailsite.AuthorSnippet', related_name='+')

    panels = [
        SnippetChooserPanel('author_snippet', AuthorSnippet),
    ]


class BlogPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('wagtailsite.BlogPage', related_name='related_links')


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('wagtailsite.BlogPage', related_name='tagged_items')


class BlogPage(Page):
    body = RichTextField()
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    date = models.DateField("Post date")
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    indexed_fields = ('body', )
    search_name = "Blog Entry"

    @property
    def blog_index(self):
        # Find blog index in ancestors
        for ancestor in reversed(self.get_ancestors()):
            if isinstance(ancestor.specific, BlogIndexPage):
                return ancestor

        # No ancestors are blog indexes,
        # just return first blog index in database
        return BlogIndexPage.objects.first()

BlogPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('date'),
    FieldPanel('body', classname="full"),
    InlinePanel(BlogPage, 'related_links', label="Related links"),
    InlinePanel(BlogPage, 'author_snippets', label="Author"),
]

BlogPage.promote_panels = [
    MultiFieldPanel(COMMON_PANELS, "Common page configuration"),
    ImageChooserPanel('feed_image'),
    FieldPanel('tags'),
]
