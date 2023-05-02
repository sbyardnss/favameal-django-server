"""View module for handling requests about restaurants"""
from rest_framework.exceptions import ValidationError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from favamealapi.models import Restaurant
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.db.models import Q, Exists

class RestaurantSerializer(serializers.ModelSerializer):
    """JSON serializer for restaurants"""

    class Meta:
        model = Restaurant
        # TODO: Add 'is_favorite' field to RestaurantSerializer
        fields = ('id', 'name', 'address', 'is_favorite')


class RestaurantView(ViewSet):
    """ViewSet for handling restuarant requests"""

    def create(self, request):
        """Handle POST operations for restaurants

        Returns:
            Response -- JSON serialized event instance
        """
        try:
            rest = Restaurant.objects.create(
                name=request.data['name'],
                address=request.data["address"]
            )
            serializer = RestaurantSerializer(rest)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single event

        Returns:
            Response -- JSON serialized game instance
        """
        try:
            restaurant = Restaurant.objects.get(pk=pk)

            # TODO: Add the correct value to the `is_favorite` property of the requested restaurant
            # Hint -- remember the 'many to many field' for referencing the records of users who have favorited this restaurant

            serializer = RestaurantSerializer(restaurant)
            return Response(serializer.data)
        except Restaurant.DoesNotExist as ex:
            return Response({"reason": ex.message}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        """Handle GET requests to restaurants resource

        Returns:
            Response -- JSON serialized list of restaurants
        """
        user = request.auth.user
        restaurants = Restaurant.objects.all()
        for restaurant in restaurants:
            restaurant.is_favorite = request.auth.user in restaurant.favorites.all()

        # TODO: Add the correct value to the `is_favorite` property of each restaurant
        # Hint -- Iterate over restaurants and look at each one's collection of favorites.
        # Remember the 'many to many field' for referencing the records of users who have favorited this restaurant

        serializer = RestaurantSerializer(restaurants, many=True)

        return Response(serializer.data)
    
    @action(methods=['POST'], detail=True)
    def favorite(self, request, pk):
        """post request for favoriting restaurant by user"""
        user = request.auth.user
        restaurant = Restaurant.objects.get(pk=pk)
        restaurant.favorites.add(user)
        return Response({'message': 'favorite added'}, status=status.HTTP_201_CREATED)

    @action(methods=['delete'], detail=True)
    def unfavorite(self, request, pk):
        """delete request for removing from favorites"""
        user=request.auth.user
        restaurant = Restaurant.objects.get(pk=pk)
        restaurant.favorites.remove(user)
        return Response({'message': 'favorite removed'}, status=status.HTTP_204_NO_CONTENT)

    # TODO: Write a custom action named `favorite` that will allow a client to
    # send a POST request to /restaurant/2/favorite and add the restaurant as a favorite

    # TODO: Write a custom action named `unfavorite` that will allow a client to
    # send a POST request to /restaurant/2/unfavorite and remove the restaurant as a favorite
