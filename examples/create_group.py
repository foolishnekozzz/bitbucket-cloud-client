#!/usr/bin/env python3

from bitbucket_cloud_client_foolishnekozzz import BitbucketWorkspace, BitbucketGroup

from os import environ

workspace = BitbucketWorkspace(name=environ.get("BITBUCKET_WORKSPACE"))
workspace.get_groups()

new_group = BitbucketGroup(name="my_new_group", workspace=workspace)
new_group.create()

#add a member to group
uuid_member = "{afdgrdgdfsgsfdgsfdgfdsgdfsg}"
new_group.add_member(uuid=uuid_member)

#print members
for i in new_group.members:
    print(i)
    print(new_group.members[i].uuid)