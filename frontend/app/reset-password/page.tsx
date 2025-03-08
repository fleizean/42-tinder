"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { toast, Toaster } from "react-hot-toast";

const ResetPasswordPage = () => {
    const router = useRouter();
    const [password, setPassword] = useState("");
    const [passwordConfirm, setPasswordConfirm] = useState("");
    const [isLoading, setLoading] = useState(false);
    const [tokenError, setTokenError] = useState(false);
    const [isValidated, setValidated] = useState(false);

    // Sayfa yüklenmeden önce token kontrolü
    useEffect(() => {
        const checkToken = async () => {
            try {
                // URL'den token ve userId'yi al
                const urlParams = new URLSearchParams(window.location.search);
                const token = urlParams.get('resetToken');
                const userId = urlParams.get('userId');

                const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/Auth/verify-reset-token`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        userId: userId,
                        resetToken: token
                    }),
                });

                if (!response.ok) {
                    setTokenError(true);
                }
                else {
                    setValidated(true);
                }
            } catch (error) {
                console.error("Check token error:", error);
                setTokenError(true);
            } finally {
                setLoading(false);
            }
        };

        checkToken();
    }, []);

    if (isLoading) {
        return (
            <section className="flex items-center justify-center h-screen">
                <div className="loader"></div>
            </section>
        );
    }

    if (tokenError) {
        return (
            <section className="relative z-10 overflow-hidden pb-16 pt-36 md:pb-20 lg:pb-28 lg:pt-[180px]">
                <div className="container">
                    <div className="-mx-4 flex flex-wrap">
                        <div className="w-full px-4">
                            <div className="shadow-three mx-auto max-w-[500px] rounded bg-white px-6 py-10 dark:bg-dark sm:p-[60px]">
                                <h3 className="mb-3 text-center text-2xl font-bold text-black dark:text-white sm:text-3xl">
                                    Şifre Sıfırlama
                                </h3>
                                <p className="mb-11 text-center text-base font-medium text-body-color">
                                    Geçersiz veya süresi dolmuş bir şifre sıfırlama bağlantısı kullandınız.
                                </p>
                                <p className="text-center text-base font-medium text-body-color">
                                    Şifre sıfırlama bağlantısı almak için{" "}
                                    <Link href="/forgot-password" className="text-primary hover:underline">
                                        buraya tıklayın
                                    </Link>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        );
    }

    const handleResetPassword = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!password || !passwordConfirm) {
            toast.error("Lütfen tüm alanları doldurunuz.");
            return;
        }

        if (password !== passwordConfirm) {
            toast.error("Şifreler eşleşmiyor.");
            return;
        }

        try {
            // URL'den token ve userId'yi al
            const urlParams = new URLSearchParams(window.location.search);
            const token = urlParams.get('resetToken');
            const userId = urlParams.get('userId');

            const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/Auth/change-password`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    UserId: userId,
                    ResetToken: token,
                    NewPassword: password
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.message || "Şifre sıfırlama başarısız.");
                return;
            }

            toast.success("Şifreniz başarıyla sıfırlandı!");
            router.push("/signin");
        } catch (error) {
            console.error("Reset password error:", error);
            toast.error("Bir hata oluştu. Lütfen daha sonra tekrar deneyiniz.");
        }
    };

    return isValidated ? (
        <>
            <Toaster position="top-right" />
            <section className="relative z-10 overflow-hidden pb-16 pt-36 md:pb-20 lg:pb-28 lg:pt-[180px]">
                <div className="container">
                    <div className="-mx-4 flex flex-wrap">
                        <div className="w-full px-4">
                            <div className="shadow-three mx-auto max-w-[500px] rounded bg-white px-6 py-10 dark:bg-dark sm:p-[60px]">
                                <h3 className="mb-3 text-center text-2xl font-bold text-black dark:text-white sm:text-3xl">
                                    Şifre Sıfırlama
                                </h3>
                                <p className="mb-11 text-center text-base font-medium text-body-color">
                                    Yeni şifrenizi belirleyin
                                </p>
                                <form onSubmit={handleResetPassword}>
                                    <div className="mb-8">
                                        <label className="mb-3 block text-sm text-dark dark:text-white">
                                            Yeni Şifre
                                        </label>
                                        <input
                                            type="password"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            placeholder="Yeni şifrenizi girin"
                                            className="border-stroke dark:text-body-color-dark dark:shadow-two w-full rounded-sm border bg-[#f8f8f8] px-6 py-3 text-base text-body-color outline-none transition-all duration-300 focus:border-primary dark:border-transparent dark:bg-[#2C303B] dark:focus:border-primary dark:focus:shadow-none"
                                        />
                                    </div>
                                    <div className="mb-8">
                                        <label className="mb-3 block text-sm text-dark dark:text-white">
                                            Şifre Tekrar
                                        </label>
                                        <input
                                            type="password"
                                            value={passwordConfirm}
                                            onChange={(e) => setPasswordConfirm(e.target.value)}
                                            placeholder="Şifrenizi tekrar girin"
                                            className="border-stroke dark:text-body-color-dark dark:shadow-two w-full rounded-sm border bg-[#f8f8f8] px-6 py-3 text-base text-body-color outline-none transition-all duration-300 focus:border-primary dark:border-transparent dark:bg-[#2C303B] dark:focus:border-primary dark:focus:shadow-none"
                                        />
                                    </div>
                                    <div className="mb-6">
                                        <button
                                            type="submit"
                                            className="shadow-submit dark:shadow-submit-dark flex w-full items-center justify-center rounded-sm bg-primary px-9 py-4 text-base font-medium text-white duration-300 hover:bg-primary/90"
                                        >
                                            Şifremi Sıfırla
                                        </button>
                                    </div>
                                </form>
                                <p className="text-center text-base font-medium text-body-color">
                                    Şifrenizi hatırladınız mı?{" "}
                                    <Link href="/signin" className="text-primary hover:underline">
                                        Giriş Yap
                                    </Link>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </>
    ) : null;
};

export default ResetPasswordPage;