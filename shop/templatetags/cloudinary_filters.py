from django import template

register = template.Library()

@register.filter(name='optimize_biscuits')
def optimize_biscuits(url, size=None):
    if not url:
        return ""
    
    if size == 'small':
        params = "w_300,h_300,c_fill,g_auto,f_auto,q_auto"
        
    if size == 'medium':
        params = "w_500,h_500,c_fill,g_auto,f_auto,q_auto"
        
    if size == 'large':
        params = "w_1200,h_1200,c_fill,g_auto,f_auto,q_auto"
    if size is None:
        params = "w_300,h_300,c_fill,g_auto,f_auto,q_auto"
    
    return url.replace("upload/", f"upload/{params}/")