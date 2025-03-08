export interface ProfileData {
    nameSurname: string;
    username: string;
    email: string;
    phoneNumber: string;
    profilePicture: string | File;
    profileFile?: File;
}