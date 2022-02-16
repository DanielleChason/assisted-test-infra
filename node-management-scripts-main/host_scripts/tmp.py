import os
import subprocess

from flask import Flask
# os.chdir("/home/dchason/projects/assisted-test-infra")

pull_secret = '{"auths":{"cloud.openshift.com":{"auth":"b3BlbnNoaWZ0LXJlbGVhc2UtZGV2K29jbV9hY2Nlc3NfZDNhNWYzMTk3NmExNDEyZmFhOTZhZDZjMDk4M2ZmMWM6OENXUDJQNkxXSFM0OTUyWElTS0w4MTA3RkZKRkdaVVAwWDUxNzZNUVVSTkkyM0kyWENSREgzQ1RWMEpDMUhZUA==","email":"dchason@redhat.com"},"quay.io":{"auth":"b3BlbnNoaWZ0LXJlbGVhc2UtZGV2K29jbV9hY2Nlc3NfZDNhNWYzMTk3NmExNDEyZmFhOTZhZDZjMDk4M2ZmMWM6OENXUDJQNkxXSFM0OTUyWElTS0w4MTA3RkZKRkdaVVAwWDUxNzZNUVVSTkkyM0kyWENSREgzQ1RWMEpDMUhZUA==","email":"dchason@redhat.com"},"registry.connect.redhat.com":{"auth":"fHVoYy1wb29sLTNhNzc4OTk5LTU0YzUtNDcwYi1hYjA1LTJhZjY5ZThmMjUyNTpleUpoYkdjaU9pSlNVelV4TWlKOS5leUp6ZFdJaU9pSXdNV1JqTm1FMFlqWmpOREkwTXpVeFlUTmtNREEzT0dFd05EQTVPV1JtTnlKOS5jaVoxWW1jRC1ySEItckFqY2ViSWk2dEZfSkNQUXgwUGJoR1d4OUVDczJiNEd4cTBiTm9sNkpBQ1IyWlotUE1HWTQtWDNiNXN5OVJNbWpYTFRIOG5pWVZuU3I0RzUxVlJUR01GYlgwS2JsMjBCSUl2V19pQVlMcmdJUjdnN3BNWFBWdGlZY1pGX01hd0txRktxaHduU3dSNkhNLVI0anlqeURTa1Fhc0ZJQXV5RWl1aHp5QkdUMm1mNDhwclpnMFcyWmlnLURXRHBDX3BibEZpX2ZYYm5mTXhjd2NPUXZsMEFoaUpSTjJPVTFRWVBwSkQ2MjJoQjJZSmp3UElRenJKcnZJMXVsRVltNnBoOTlkY2tvU2VuTlNzb2ZhS1JPT1lPUGh1eVB6NzhONnRyTlVCWVg4WER4OVZ2Wk50UGkydWVPNjAzVHpMYkZaOFRkSXVHeGZRX0pfZFZxMFJrWGplR0duS2NUeXVlUlVhQ1c2Y194OTlQOE9VdWdLcmtSSWJtOHMyYk1qUzFpMHRuamtJT2tXalFoN28xUTVneERSMW1hTjR1bnBFcGNIS3VBV0luYloxaHZhM004WDZ2bzc5anJTOGRQdGloc2EwZGlfWi1nNTZsSFdNOXdWcnFKX3BXd3h0MllhRnNoaWRhdFkyX3pycllTblFGZXRyeEJTMnNIalJ4clpCVldGZFM0ZzU1NjJKTkRtQzB4QVk3MmRiMmE1Y3BoWUE3c0JJSXBBT1dMczNncUV1U3VIZzdpUlIzRUtFbjR0dVZEMU1LS2t5WXU1eEFFNV9icGpIdXNEcHJUalRXWTZ5aWlHMFc4bVZrRndJNDkwWjV1TllQR2ZQUWtOdmhCakpaNDRBVUxSbHc2Mk12Q0lENk9TVTlUY2FSa1RWRmNkTzZHWQ==","email":"dchason@redhat.com"},"registry.redhat.io":{"auth":"fHVoYy1wb29sLTNhNzc4OTk5LTU0YzUtNDcwYi1hYjA1LTJhZjY5ZThmMjUyNTpleUpoYkdjaU9pSlNVelV4TWlKOS5leUp6ZFdJaU9pSXdNV1JqTm1FMFlqWmpOREkwTXpVeFlUTmtNREEzT0dFd05EQTVPV1JtTnlKOS5jaVoxWW1jRC1ySEItckFqY2ViSWk2dEZfSkNQUXgwUGJoR1d4OUVDczJiNEd4cTBiTm9sNkpBQ1IyWlotUE1HWTQtWDNiNXN5OVJNbWpYTFRIOG5pWVZuU3I0RzUxVlJUR01GYlgwS2JsMjBCSUl2V19pQVlMcmdJUjdnN3BNWFBWdGlZY1pGX01hd0txRktxaHduU3dSNkhNLVI0anlqeURTa1Fhc0ZJQXV5RWl1aHp5QkdUMm1mNDhwclpnMFcyWmlnLURXRHBDX3BibEZpX2ZYYm5mTXhjd2NPUXZsMEFoaUpSTjJPVTFRWVBwSkQ2MjJoQjJZSmp3UElRenJKcnZJMXVsRVltNnBoOTlkY2tvU2VuTlNzb2ZhS1JPT1lPUGh1eVB6NzhONnRyTlVCWVg4WER4OVZ2Wk50UGkydWVPNjAzVHpMYkZaOFRkSXVHeGZRX0pfZFZxMFJrWGplR0duS2NUeXVlUlVhQ1c2Y194OTlQOE9VdWdLcmtSSWJtOHMyYk1qUzFpMHRuamtJT2tXalFoN28xUTVneERSMW1hTjR1bnBFcGNIS3VBV0luYloxaHZhM004WDZ2bzc5anJTOGRQdGloc2EwZGlfWi1nNTZsSFdNOXdWcnFKX3BXd3h0MllhRnNoaWRhdFkyX3pycllTblFGZXRyeEJTMnNIalJ4clpCVldGZFM0ZzU1NjJKTkRtQzB4QVk3MmRiMmE1Y3BoWUE3c0JJSXBBT1dMczNncUV1U3VIZzdpUlIzRUtFbjR0dVZEMU1LS2t5WXU1eEFFNV9icGpIdXNEcHJUalRXWTZ5aWlHMFc4bVZrRndJNDkwWjV1TllQR2ZQUWtOdmhCakpaNDRBVUxSbHc2Mk12Q0lENk9TVTlUY2FSa1RWRmNkTzZHWQ==","email":"dchason@redhat.com"}}}'


def start_vms_on_background():
    print('hi')
    # subprocess.check_output("make deploy_nodes",
    #                         env={'CLUSTER_ID': cluster_id, 'NUM_MASTERS': num_of_masters,
    #                              'NUM_WORKERS': num_of_workers, 'PULL_SECRET': pull_secret})
    res = subprocess.run(['skipper', 'make', '-i', '_test'], shell=True,
                           env={'CLUSTER_ID': '9edde3a3-bf90-45e3-a6f9-6b0437ec529c', 'NUM_MASTERS': '3',
                                'NUM_WORKERS': '0',
                                'PULL_SECRET': pull_secret, 'TEST_TEARDOWN':'no', 'TEST':'./src/tests/test_targets.py',  'TEST_FUNC':'test_target_deploy_nodes'}, cwd="/home/dchason/projects/assisted-test-infra")
    print(res)

if __name__ == '__main__':
    start_vms_on_background()
