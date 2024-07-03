# JWT Token Encryption Keys

In this folder, the files `.jwt.private.env` and `.jwt.public.env` should be located.

How to create them:

```sh
cd jwt_keys # run commands from this folder
```

Creating `.jwt.private.env`:
```sh
openssl genpkey -algorithm RSA -out private_key.pem
echo 'JWT_PRIVATE_KEY="' > .jwt.private.env
sed ':a;N;$!ba;s/\n/\\n/g' private_key.pem | awk '{print $0 "\\n"}' >> .jwt.private.env
echo '"' >> .jwt.private.env

tr -d '\n' < .jwt.private.env > .jwt.private.env.tmp && mv .jwt.private.env.tmp .jwt.private.env
```

Creating `.jwt.public.env`:
```sh
openssl rsa -pubout -in private_key.pem -out public_key.pem
echo 'JWT_PUBLIC_KEY="' > .jwt.public.env
sed ':a;N;$!ba;s/\n/\\n/g' public_key.pem | awk '{print $0 "\\n"}' >> .jwt.public.env
echo '"' >> .jwt.public.env

tr -d '\n' < .jwt.public.env > .jwt.public.env.tmp && mv .jwt.public.env.tmp .jwt.public.env
```
You can delete the `private_key.pem` and `public_key.pem` files:
```sh
rm private_key.pem public_key.pem
```