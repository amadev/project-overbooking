# project-overbooking

## description

The main goal of this project is to choose optimal algorithm for
overbooking logic.
There is project hierarchy with limit and used resource values per
each node of the tree. An overbooking term in this context means that sum
of subnodes limit values can be greater than parent limit value.

Naive algorithm is just checking that sum of node used resources and used
resources of all subnodes don't exceed node resource limit.
If it's okay for current node we should check same conditions for
the parent node and so on. Hence, for a happy path we should traverse all
tree.

The question was how we should get project hierarchy from DB.
It was proposed to download all tree in one SQL request.
As it can be a quite heavy request we must determine some
borders within it would be appropriate.

## installation & run

```
$ pip install ete3 nose pandas matplotlib
$ cd project-overbooking
$ nosetests project_overbooking.tests
$ POB_CONN_STR=mysql://test_user:test_pass@localhost:9000/test_db \
    nosetests project_overbooking.performance
```

## performance test

The workflow of the performance test is following.
With the help of ETE library the random tree is generated with the particular
amount of leafs (the actual amount of projects is almost two times
more). After that, the farthest leaf is chosen. For that leaf
the procedure of checking limits is applied taking into account
that no limits should be exceeded and all tree should be traversed.

The results of run can be presented as the table:

```
| run number | time, ms, 20 nodes | time, ms, 200 nodes | time, ms, 2000 nodes |
|------------+--------------------+---------------------+----------------------|
|          0 |             59.092 |              77.809 |              958.915 |
|          1 |             54.872 |              73.398 |              449.773 |
|          2 |             53.749 |              70.709 |              365.435 |
|          3 |             54.326 |              66.505 |              321.229 |
|          4 |             54.961 |              67.188 |              310.871 |
|          5 |             55.461 |              68.659 |              275.498 |
|          6 |             54.844 |             116.461 |              258.471 |
|          7 |             58.944 |              89.317 |              248.072 |
|          8 |             55.778 |              66.141 |              246.983 |
|          9 |             55.902 |              66.335 |              206.991 |
|         10 |             54.514 |              70.943 |              224.342 |
...
```

Or as the diagram:
![overbooking limit processing time](/performance_report.png)

## conclusion

As result I can propose that such algorithm can be used
for installation up to 2000 projects in hierarcy.
Request processing time teoretically will be increased up
to 1 sec with median increase ~300ms.
