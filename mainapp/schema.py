import graphene
from graphene_django import DjangoObjectType
from .models import City, Component
from graphql import GraphQLError


# list of Citys
class CityType(DjangoObjectType):
    class Meta:
        model = City
        fields = ('id', 'city')


# list of Components
class ComponentType(DjangoObjectType):
    class Meta:
        model = Component
        fields = ('id', 'company', 'description', 'city')


# Create City
class CreateCity(graphene.Mutation):

    class Arguments:
        city = graphene.String()
    
    city = graphene.Field(CityType)

    @classmethod
    def mutate(cls, root, info, **city_data):
        try:
            obj = City(
                city=city_data.get('city')
            )

            obj.save()
            return CreateCity(city=obj)
        except Exception as ex:
            return GraphQLError("City already exist")


# Group input for Component
class GroupInput(graphene.InputObjectType):
    id = graphene.ID(required=True)


# Create Component
class CreateRecord(graphene.Mutation):

    class Arguments:
        company = graphene.String()
        description = graphene.String()
        city_id = graphene.List(GroupInput, required=True)

    component = graphene.Field(ComponentType)

    @classmethod
    def mutate(cls, root, info, **component_data):

        try:
            obj = Component(
                company=component_data['company'],
                description=component_data['description'],
            )
            obj.save()
            for i in component_data['city_id']:
                obj.city.add(i['id'])
            return CreateRecord(component=obj)
        except:
            return GraphQLError("Company already exist")


# update City
class UpdateCity(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        city = graphene.String()
    city = graphene.Field(CityType)

    @classmethod
    def mutate(cls, root, info, id, **update_data):
        city = City.objects.filter(id=id)
        if city:
            if City.objects.filter(city = update_data['city']).exists():
                return GraphQLError("city name is allready exist.")
            try:
                city.update(city=update_data['city'])
                return UpdateCity(city=city.first())
            except:
                return GraphQLError("Something is wrong")
        else:
            return GraphQLError("City with given ID does not exist")


# update Component
class UpdateRecord(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        company = graphene.String()
        description = graphene.String()
        city_id = graphene.List(GroupInput, required=True)
    
    component = graphene.Field(ComponentType)

    @classmethod
    def mutate(cls, root, info, id, **update_data):
        obj = Component.objects.filter(id=id)
        if obj:
            try:
                obj.update(
                    company=update_data['company'],
                    description=update_data['description'],
                )

                data = obj[0].city.all()
                current_selected = []
                for i in data:
                    current_selected.append(i.id)

                recent_record = []
                for i in update_data['city_id'] :
                    recent_record.append(int(i["id"]))
            
                final_record = list(set(current_selected+recent_record))

                for j in final_record:

                    if j not in  recent_record:
                        obj[0].city.remove(str(j))
                    else:
                        obj[0].city.add(str(j))

                return UpdateRecord(component=obj.first())
            except Exception as e:
                print(e)
                return GraphQLError("Company name already exist...")
        else:
            return GraphQLError("Component with given ID does not exist.")


# Delete City
class DeleteCity(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    msg = graphene.String()
    city = graphene.Field(CityType)

    @classmethod
    def mutate(cls, root, info, id):
        try:
            city = City.objects.get(id=id)
            city.delete()
            return DeleteCity(msg = 'City deleted')
        except:
            return GraphQLError("City was not define.")


# Delete Component
class DeleteRecord(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
    msg = graphene.String()
    component = graphene.Field(ComponentType)

    @classmethod
    def mutate(cls, root, info, id):
        try:
            obj = Component.objects.get(id=id)
            obj.delete()
            return DeleteRecord(msg = 'Component delete')
        except:
            return GraphQLError("Component was not define.")
        

class SelectCityDelete(graphene.Mutation):
    class Arguments:
        city_id = graphene.List(GroupInput, required=True)
    
    msg = graphene.String()
    city = graphene.Field(CityType)

    @classmethod
    def mutate(cls,root,info,city_id):
        try:
            for i in city_id:
                City.objects.filter(id=int(i['id'])).delete()
            return SelectCityDelete(msg = 'All Selected Citys Deleted.')
        except:
            return GraphQLError('Somthing was wrong.')



class SelectComponentDelete(graphene.Mutation):
    class Arguments:
        component_id = graphene.List(GroupInput, required=True)
    
    msg = graphene.String()
    component = graphene.Field(ComponentType)

    @classmethod
    def mutate(cls,root,info,component_id):
        try:
            for i in component_id:
                Component.objects.filter(id=int(i['id'])).delete()
            return SelectComponentDelete(msg = 'All Selected Components Deleted.')
        except:
            return GraphQLError('Somthing was wrong.')





# graphql query of get list for models items
class Query(graphene.ObjectType):
    all_city = graphene.List(CityType)
    city_by_id = graphene.Field(CityType, id=graphene.String())
    all_component = graphene.List(ComponentType)
    component_by_id = graphene.Field(ComponentType, id=graphene.String())

    def resolve_all_city(root, info):
        return City.objects.all().order_by('id')

    def resolve_city_by_id(root, info, id):
        return City.objects.get(id=id)

    def resolve_all_component(root, info):
        return Component.objects.all().order_by('id')

    def resolve_component_by_id(root, info, id):
        return Component.objects.get(id=id)


# graphql mutation of create update delete for models items
class Mutation(graphene.ObjectType):
    create_city = CreateCity.Field()
    update_city = UpdateCity.Field()
    delete_city = DeleteCity.Field()
    create_record = CreateRecord.Field()
    update_record = UpdateRecord.Field()
    delete_record = DeleteRecord.Field()
    select_city_delete = SelectCityDelete.Field()
    select_component_delete = SelectComponentDelete.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
