"""View module for handling requests about meals"""
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from favamealapi.models import Meal, MealRating, Restaurant, FavoriteMeal
from favamealapi.views.restaurant import RestaurantSerializer
from django.db.models import Avg

class MealSerializer(serializers.ModelSerializer):
    """JSON serializer for meals"""
    restaurant = RestaurantSerializer(many=False)

    class Meta:
        model = Meal
        # TODO: Add 'user_rating', 'avg_rating', 'is_favorite' fields to MealSerializer
        fields = ('id', 'name', 'restaurant', 'is_favorite', 'mealrating', 'rating', 'avg_rating')
        depth = 1


class MealView(ViewSet):
    """ViewSet for handling meal requests"""

    def create(self, request):
        """Handle POST operations for meals

        Returns:
            Response -- JSON serialized meal instance
        """
        try:
            meal = Meal.objects.create(
                name=request.data["name"],
                restaurant=Restaurant.objects.get(
                    pk=request.data["restaurant_id"])
            )
            serializer = MealSerializer(meal)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single meal

        Returns:
            Response -- JSON serialized meal instance
        """
        try:
            meal = Meal.objects.get(pk=pk)

            # TODO: Get the rating for current user and assign to `user_rating` property
            user_rating = MealRating.objects.get(
                user=request.auth.user, meal=meal)
            # TODO: Get the average rating for requested meal and assign to `avg_rating` property

            # TODO: Assign a value to the `is_favorite` property of requested meal

            serializer = MealSerializer(meal)
            return Response(serializer.data)
        except Meal.DoesNotExist as ex:
            return Response({"reason": ex.message}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests to meals resource

        Returns:
            Response -- JSON serialized list of meals
        """
        meals = Meal.objects.annotate(avg_rating=Avg('mealrating__rating'))
        
        for meal in meals:
            meal.is_favorite = request.auth.user in meal.favorites.all()
            # rating_sum = 0
            # connected_ratings = MealRating.objects.filter(meal=meal)
            # print(connected_ratings)
            try:
                rating_object = MealRating.objects.get(user=request.auth.user, meal=meal)
                meal.rating = rating_object.rating
            except MealRating.DoesNotExist:
                meal.rating = 0
        
            # print(connected_ratings.rating)
        # meal.avg_rating = sum(connected_ratings.rating)//len(connected_ratings)

        # TODO: Get the rating for current user and assign to `user_rating` property
            # meal.user_rating = MealRating.objects.get(user=request.auth.user, meal= meal)
        # TODO: Get the average rating for each meal and assign to `avg_rating` property

        # TODO: Assign a value to the `is_favorite` property of each meal

        serializer = MealSerializer(meals, many=True)

        return Response(serializer.data)

    # TODO: Add a custom action named `rate` that will allow a client to send a
    #  POST and a PUT request to /meals/3/rate with a body of..
    #       {
    #           "rating": 3
    #       }
    # If the request is a PUT request, then the method should update the user's rating instead of creating a new one

    # TODO: Add a custom action named `favorite` that will allow a client to send a
    #  POST request to /meals/3/favorite and add the meal as a favorite
    @action(methods=['post'], detail=True)
    def rate(self, request, pk):
        """post request for meal rating"""
        # user = request.auth.user
        meal = Meal.objects.get(pk=pk)
        user_rating = request.data['rating']
        rating = MealRating.objects.create(
            user=request.auth.user, meal=meal, rating=user_rating)
        return Response({'message': 'rating added'}, status=status.HTTP_201_CREATED)

    @action(methods=['put'], detail=True)
    def rate(self, request, pk):
        """put request for meal rating"""
        meal = Meal.objects.get(pk=pk)
        user_rating = request.data['rating']
        rating = MealRating.objects.get(meal=meal, user=request.auth.user)
        rating.rating = user_rating
        rating.save()
        return Response({'message': 'rating updated'}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True)
    def favorite(self, request, pk):
        """post request for mealfavorite"""
        user = request.auth.user
        meal = Meal.objects.get(pk=pk)
        meal.favorites.add(user)
        return Response({'message': 'favorite added'}, status=status.HTTP_201_CREATED)


    @action(methods=['delete'], detail=True)
    def unfavorite(self, request, pk):
        """delete favorite request"""
        user = request.auth.user
        meal = Meal.objects.get(pk=pk)
        meal.favorites.remove(user)
        return Response({'message': 'favorite removed'}, status=status.HTTP_204_NO_CONTENT)
    # TODO: Add a custom action named `unfavorite` that will allow a client to send a
    # DELETE request to /meals/3/unfavorite and remove the meal as a favorite
