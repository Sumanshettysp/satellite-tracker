from iommi import Page, html

def test_view(request):
    return Page(
        title="Test Page",
        parts__header=html.h1("TEST PAGE - Iommi Works!"),
        parts__content=html.p("If you see this, everything is working."),
        parts__link=html.a("Go Home", attrs={'href': '/'})
    )