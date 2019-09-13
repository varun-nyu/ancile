import graphene
from graphene_django.types import DjangoObjectType
from ancile.web.dashboard import models
from ancile.web.api.visualizer import parse_policy

class UserType(DjangoObjectType):
    class Meta:
        model = models.User
        only_fields = ('username', 'first_name', 'last_name', 'email', 'is_superuser', 'is_developer', )

class ScopeType(DjangoObjectType):
    class Meta:
        model = models.Scope


class TokenType(DjangoObjectType):
    
    class Meta:
        model = models.Token
        only_fields = ('id', 'provider', 'expires_at', 'scopes', )
        

class ProviderType(DjangoObjectType):
    scopes = graphene.List(ScopeType)
    token = graphene.Field(TokenType)
    
    class Meta:
        model = models.DataProvider
        exclude_fields = ('clientId', 'clientSecret', 'accessTokenUrl', 'authUrl')

    def resolve_scopes(self, info, **args):
        return models.Scope.objects.filter(provider=self)

    def resolve_token(self, info, **args):
        return models.Token.objects.filter(provider=self, user=info.context.user).first()

class DeleteToken(graphene.Mutation):
    class Arguments:
        token = graphene.Int()
    
    ok = graphene.Boolean()
    
    def mutate(root, info, token):
        token = models.Token.objects.get(id=token)
        token.delete()
        return DeleteToken(ok=True)

class PolicyType(DjangoObjectType):
    
    graph = graphene.String()
    
    class Meta:
        model = models.Policy
        only_fields = ('provider', 'text')
        
    def resolve_graph(self, info, **args):
        return parse_policy(self.text)

class PermissionGroupType(DjangoObjectType):
    
    class Meta:
        model = models.PermissionGroup
        only_fields = ("id", "name", "description", "scopes", )
    
    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter(approved=True)

class AppType(DjangoObjectType):
    
    policies = graphene.List(PolicyType)
    groups = graphene.List(PermissionGroupType)
    token = graphene.String()

    class Meta:
        model = models.App
        only_fields = ('id', 'name', 'description', 'developers', )
    
    def resolve_policies(self, info, **args):
        policies = models.Policy.objects.filter(user=info.context.user, app=self)
        return policies
    
    def resolve_groups(self, info, **args):
        permission_groups = models.PermissionGroup.objects.filter(app=self)
        return permission_groups
    
    def resolve_developers(self, info, **args):
        if info.context.user.is_developer:
            return self.developers

    def resolve_token(self, info, **args):
        if info.context.user.is_developer:
            return self.encoded_salt

class DeleteApp(graphene.Mutation):
    class Arguments:
        app = graphene.Int()
    
    ok = graphene.Boolean()
    
    def mutate(root, info, app):
        models.Policy.objects.filter(app__id=app, user=info.context.user).delete()
        return DeleteApp(ok=True)

class AddPermissionGroup(graphene.Mutation):
    class Arguments:
        app = graphene.Int()
        group = graphene.Int()
        
    ok = graphene.Boolean()
    
    def mutate(root, info, group, app):
        app = models.App.objects.get(id=app)
        perm_group = models.PermissionGroup.objects.get(id=group, app=app)

        needed_policies = models.PolicyTemplate.objects.filter(group=perm_group,
                                                               app=app)

        new_policies = []

        for policy in needed_policies:
            if not models.Token.objects.filter(provider=policy.provider):
                raise Exception("Provider not found")

            new_policy = models.Policy(
                text=policy.text,
                provider=policy.provider,
                user=info.context.user,
                app=app,
                active=True
            )

            new_policies.append(new_policy)

        for policy in new_policies:
            policy.save()
        
        return AddPermissionGroup(ok=True)

class CreatePermissionGroup(graphene.Mutation):
    class Arguments:
        app = graphene.Int()
        name = graphene.String()
        description = graphene.String()
        approved = graphene.Boolean(default_value=False)

    ok = graphene.Boolean()
    error = graphene.String()

    def mutate(self, info, approved, description, name, app):
        try:
            app = models.App.objects.get(id=app)
        except models.app.DoesNotExist:
            return CreatePermissionGroup(ok=False, error="App not found")

        approved = approved if info.context.user.is_superuser else False

        if info.context.user.is_superuser or (info.context.user.is_developer and info.context.user in app.developers):
            if name and description:
                group = models.PermissionGroup(name=name,
                                               description=description,
                                               app=app,
                                               approved=approved)
                group.save()
                return CreatePermissionGroup(ok=True)
            return CreatePermissionGroup(ok=False, error="Name and/or description missing")
        return CreatePermissionGroup(ok=False, error="Insufficient permissions")

class AddApp(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        description = graphene.String()
    
    ok = graphene.Boolean()
    error = graphene.String()
    
    def mutate(root, info, name, description):
        if info.context.user.is_developer:
            if not models.App.objects.filter(name=name):
                app = models.App(name=name, description=description)
                app.save()
                app.developers.add(info.context.user)
                return AddApp(ok=True)
            return AddApp(ok=False, error="App with same name already exists")
        return AddApp(ok=False, error="Insufficient privileges")


class Mutations(graphene.ObjectType):
    delete_token = DeleteToken.Field()
    delete_app = DeleteApp.Field()
    add_permission_group = AddPermissionGroup.Field()
    add_app = AddApp.Field()
    create_permission_group = CreatePermissionGroup.Field()

class Query(object):
    all_providers = graphene.List(ProviderType)
    all_scopes = graphene.List(ScopeType)
    all_tokens = graphene.List(TokenType)
    all_apps = graphene.List(AppType)
    developer_apps = graphene.List(AppType, id=graphene.Int(default_value=-1))
    current_user = graphene.Field(UserType)

    def resolve_all_providers(self, info, **args):
        return models.DataProvider.objects.all()
    
    def resolve_all_scopes(self, info, **args):
        return models.Scope.objects.all()
    
    def resolve_all_tokens(self, info, **args):
        return models.Token.objects.filter(user=info.context.user)
    
    def resolve_all_apps(self, info, **args):
        return models.App.objects.all()
    
    def resolve_developer_apps(self, info, id, **args):
        if info.context.user.is_developer:
            if id < 0:
                return models.App.objects.filter(developers=info.context.user)
        return models.App.objects.filter(id=id, developers=info.context.user)

    def resolve_current_user(self, info, **args):
        return info.context.user