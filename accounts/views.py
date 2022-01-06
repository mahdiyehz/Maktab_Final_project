from django.shortcuts import redirect


def login_success(request):
    if request.user.is_superuser:
        return redirect("food_list")
    elif request.user.is_staff:
        return redirect('home')  # todo: in next phase edit to manager_panel
    else:
        return redirect("home")
