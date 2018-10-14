"""
1) Download repository containing Dockerfile into temp directory.
2) Copy across any additional files.
3) Change the FROM in the Dockerfile.
4) Add part Dockerfiles at any points in the original. 
5) Remove lines of the original Dockerfile
6) Return new Dockerfile.
"""

Note: makes a temp copy of the repo
