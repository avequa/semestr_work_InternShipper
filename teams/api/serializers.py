from rest_framework import serializers
from teams.models import Team, TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):
    """Участник команды с данными пользователя"""

    username = serializers.CharField(source='student.user.username')
    full_name = serializers.CharField(source='student.user.get_full_name')

    class Meta:
        model = TeamMember
        fields = ['id', 'username', 'full_name']


class TeamSerializer(serializers.ModelSerializer):
    """Информация о команде и ее участниках"""

    captain = serializers.CharField(source='captain.user.username')
    members = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'captain', 'members']

    def get_members(self, obj):
        members = TeamMember.objects.filter(team=obj)
        return TeamMemberSerializer(members, many=True).data